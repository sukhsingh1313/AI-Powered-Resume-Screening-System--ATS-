import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from django.contrib.auth import get_user_model
from .models import Job, Resume, Application
from .utils import extract_text_from_pdf, calculate_match_score, extract_contact_info, generate_interview_questions
from .forms import JobForm
from django.contrib.auth import logout


User = get_user_model() 

def job_list(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) | 
            Q(required_skills__icontains=query) | 
            Q(description__icontains=query)
        )
    return render(request, 'core/job_list.html', {'jobs': jobs, 'query': query})

def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        resume_file = request.FILES.get('resume_file')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        
        if resume_file and email and full_name:
            # 👇 NAYA UPDATE: Get or Create user, aur hamesha Full Name save karo
            candidate_user, created = User.objects.get_or_create(username=email)
            candidate_user.email = email
            candidate_user.first_name = full_name # Name strictly save kar rahe hain
            candidate_user.save()
            
            resume, created = Resume.objects.get_or_create(user=candidate_user)
            resume.resume_file = resume_file
            resume.save()
            
            text = extract_text_from_pdf(resume.resume_file.path)
            resume.parsed_text = text
            contacts = extract_contact_info(text)
            
            resume.contact_email = contacts.get('email') if contacts.get('email') != 'Not Found' else email
            resume.phone_number = contacts.get('phone', '')
            resume.linkedin_url = contacts.get('linkedin', '')
            resume.save()
            
            jd_context = f"{job.description} {job.required_skills}"
            score = calculate_match_score(text, jd_context)
            ai_questions = generate_interview_questions(text, job.required_skills)
            
            Application.objects.create(
                job=job,
                candidate=candidate_user,
                match_score=score,
                ai_interview_questions=ai_questions
            )
            
            messages.success(request, f"Application Submitted! Your AI Match Score is {score}%.")
            return redirect('job_list')
        else:
            messages.error(request, "Please provide Name, Email, and upload a valid PDF.")

    return render(request, 'core/apply_job.html', {'job': job})

@login_required
def dashboard(request):
    if request.user.is_recruiter:
        applications = Application.objects.all().order_by('-match_score')
        total_apps = applications.count()
        avg_score = applications.aggregate(Avg('match_score'))['match_score__avg'] or 0
        active_jobs = Job.objects.filter(is_active=True).count()
        
        # Dashboard context
        context = {
            'applications': applications,
            'total_apps': total_apps,
            'avg_score': round(avg_score, 1),
            'active_jobs': active_jobs
        }
        return render(request, 'core/hr_dashboard.html', context)
    else:
        applications = Application.objects.filter(candidate=request.user).order_by('-applied_at')
        return render(request, 'core/candidate_dashboard.html', {'applications': applications})

@login_required
def application_detail(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    if not request.user.is_recruiter and request.user != application.candidate:
        messages.error(request, "Permission Denied.")
        return redirect('dashboard')
        
    required_skills = [skill.strip().lower() for skill in application.job.required_skills.split(',')]
    resume_text = application.candidate.resume.parsed_text.lower() if application.candidate.resume.parsed_text else ""
    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill and skill in resume_text:
            matched_skills.append(skill.title())
        elif skill:
            missing_skills.append(skill.title())

    total_skills = len(matched_skills) + len(missing_skills)
    gap_percentage = int((len(matched_skills) / total_skills) * 100) if total_skills > 0 else 0

    context = {
        'application': application,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'gap_percentage': gap_percentage,
        'total_skills': total_skills
    }
    return render(request, 'core/analysis_report.html', context)

@login_required
def update_status(request, app_id, new_status):
    if not request.user.is_recruiter:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')
    application = get_object_or_404(Application, id=app_id)
    application.status = new_status
    application.save()
    
    candidate_name = application.candidate.first_name if application.candidate.first_name else application.candidate.username
    messages.success(request, f"Status for {candidate_name} updated to {new_status.title()}!")
    return redirect('dashboard')

@login_required
def create_job(request):
    if not request.user.is_recruiter:
        messages.error(request, "Only HR/Recruiters can post jobs.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "New Job Posted Successfully! 🚀")
            return redirect('dashboard')
    else:
        form = JobForm()
    return render(request, 'core/create_job.html', {'form': form})

@login_required
def export_csv(request):
    if not request.user.is_recruiter:
        messages.error(request, "Only HR can download reports.")
        return redirect('dashboard')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ATS_Candidates_Report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Rank', 'Candidate Name', 'Email', 'Phone', 'Job Applied', 'AI Match Score (%)', 'Status', 'Applied Date'])
    applications = Application.objects.all().order_by('-match_score')
    for index, app in enumerate(applications, start=1):
        email = app.candidate.resume.contact_email if hasattr(app.candidate, 'resume') and app.candidate.resume.contact_email else app.candidate.email
        phone = app.candidate.resume.phone_number if hasattr(app.candidate, 'resume') and app.candidate.resume.phone_number else 'N/A'
        
        candidate_name = app.candidate.first_name if app.candidate.first_name else app.candidate.username
        writer.writerow([
            index,
            candidate_name,
            email,
            phone,
            app.job.title,
            f"{app.match_score}%",
            app.get_status_display(),
            app.applied_at.strftime("%Y-%m-%d %H:%M")
        ])
    return response


def custom_logout(request):
    """Custom view for smooth logout"""
    logout(request)
    messages.info(request, "You have been securely logged out.")
    return redirect('job_list')



from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_secret_admin(request):
    """Hidden URL to create superuser bypass"""
    User = get_user_model()
    
    # Check agar pehle se bana hua hai
    if User.objects.filter(email='admin@ats.com').exists():
        return HttpResponse("<h1>Admin pehle se bana hua hai! 😎</h1><p>Jakar login karo.<br><b>Email/Username:</b> admin@ats.com ya hradmin<br><b>Password:</b> Admin@1234</p>")
    
    try:
        # Trick 1: Agar CustomUser me email hi username hai
        User.objects.create_superuser(email='admin@ats.com', password='Admin@1234')
        return HttpResponse("<h1>SUCCESS! 🔥</h1><p>Naya admin ban gaya.<br><b>Login Email:</b> admin@ats.com<br><b>Password:</b> Admin@1234</p>")
    except Exception as e1:
        try:
            # Trick 2: Agar standard model jaisa hai jisme username chahiye
            User.objects.create_superuser('hradmin', 'admin@ats.com', 'Admin@1234')
            return HttpResponse("<h1>SUCCESS! 🔥</h1><p>Naya admin ban gaya.<br><b>Login Username:</b> hradmin<br><b>Password:</b> Admin@1234</p>")
        except Exception as e2:
            # Agar koi aur custom field required hai toh screen par error dikh jayega
            return HttpResponse(f"<h1>Error Aaya! 😢</h1><p>Details: {e2}</p>")