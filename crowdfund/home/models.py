from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='project_pictures/')
    total_target = models.DecimalField(max_digits=10, decimal_places=2)
    total_donated = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # tags = models.ManyToManyField('Tag', blank=True)
    tags = models.ManyToManyField(Tag, related_name='projects')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # creator = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    def can_be_cancelled(self):
        # Check if donations are less than 25% of the target
        return self.total_donated < (self.total_target / 4)
    # def getimage(self):
    #     return f'/media/{self.image}'

    
class Donation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='donations')
    # donor = models.ForeignKey(User, on_delete=models.CASCADE)
    donor = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor} donated {self.amount} to {self.project}"
    
class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user} on {self.project}"
    
class Reply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.CharField(max_length=255)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply by {self.user} on {self.comment}"

class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    user = models.CharField(max_length=255)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()  # Rating score between 1 and 5
    rated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} rated {self.project} with {self.score}"

    # class Meta:
    #     unique_together = ('project', 'user')  # Ensure a user can only rate a project once

   
