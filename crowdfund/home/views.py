from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib import messages

# Create your views here.

# def create_project(request):
#     if request.method == 'POST':
#         form = ProjectForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('project_detail', pk=project.pk)
#     else:
#         form = ProjectForm()
#     return render(request, 'create_project.html', {'form': form})
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            # project.creator = request.user  # Assuming the user is logged in
            project.save()
            form.save_m2m()  # To save many-to-many relationships (tags)
            
            # # Save multiple images
            # for image in request.FILES.getlist('images'):
            #     ProjectImage.objects.create(project=project, image=image)

            return redirect('project_detail', pk=project.pk)  # Redirect to the project details page
    else:
        form = ProjectForm()
    return render(request, 'create_project.html', {'form': form})


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    donations = project.donations.all()
    comments = project.comments.all()  # Get all comments and their replies
    donation_form = DonationForm()
    comment_form = CommentForm()
    reply_form = ReplyForm()
    rating_form = RatingForm()

    if request.method == 'POST':
        if 'donate' in request.POST:
         donation_form = DonationForm(request.POST)
         if donation_form.is_valid():
            donation = donation_form.save(commit=False)
            donation.donor = request.user  # Assuming the user is logged in
            donation.project = project
            donation.save()

            # Update the total donated amount in the project
            project.total_donated += donation.amount
            project.save()

            return redirect('project_detail', pk=project.pk)

        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.project = project
                comment.save()
                return redirect('project_detail', pk=project.pk)

        elif 'reply' in request.POST:
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.user = request.user
                reply.comment_id = request.POST.get('comment_id')  # Get the ID of the comment being replied to
                reply.save()
                return redirect('project_detail', pk=project.pk)
        elif 'rate' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.user = request.user
                rating.project = project

                # Update the user's existing rating or create a new one
                existing_rating = Rating.objects.filter(user=request.user, project=project).first()
                if existing_rating:
                    existing_rating.score = rating_form.cleaned_data['score']
                    existing_rating.save()
                else:
                    rating.save()
                return redirect('project_detail', pk=project.pk)
    avg_rating = project.ratings.aggregate(average=models.Avg('score'))['average'] or 0
    similar_projects = Project.objects.filter(tags__in=project.tags.all()).exclude(id=project.id).distinct()[:4]

    return render(request, 'project_detail.html', {
        'project': project,
        'donation_form': donation_form,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'donations': donations,
        'comments': comments,
        'rating_form': rating_form,
        # 'user_rating': user_rating,
        'avg_rating': avg_rating,
        'similar_projects': similar_projects,
    })

def cancel_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.can_be_cancelled():
        project.delete()
        messages.success(request, 'Project has been cancelled successfully.')
    else:
        messages.error(request, 'Project cannot be cancelled as donations exceed 25% of the target.')

    # return redirect('home')
    return redirect('create_project')
