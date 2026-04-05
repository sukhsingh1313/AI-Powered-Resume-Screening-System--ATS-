from django.db import models
from django.conf import settings

# Custom User model reference
User = settings.AUTH_USER_MODEL

class Job(models.Model):
    """HR through dashboard jobs post karega"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma separated skills, e.g., Python, Django, React")
    min_experience = models.IntegerField(default=0, help_text="Minimum experience in years")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Resume(models.Model):
    """Candidate ka resume aur extracted data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume')
    resume_file = models.FileField(upload_to='resumes/')
    parsed_text = models.TextField(blank=True, null=True)
    
    # Smart Contact Info (Regex se extract kiya hua)
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"

class Application(models.Model):
    """Job aur Candidate ka connection + AI Analysis"""
    
    # Dashboard dropdown aur logic ke liye consistent choices
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interviewing'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    match_score = models.FloatField(default=0.0)
    
    # AI Generated Interview Questions (Resume vs JD)
    ai_interview_questions = models.TextField(blank=True, null=True)
    
    # Hiring Pipeline Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='applied'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} -> {self.job.title}"