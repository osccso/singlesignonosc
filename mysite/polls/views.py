import json
from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from polls import models
from polls.forms.user import ProfileForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def index(request):
    context = {
        'polls': []
    }
    # # Optional solution in case you have a lot of polls 
    # # bring all needed information
    # answers = models.Answer.objects.all().select_related('poll','user').order_by('poll')
    # # # get every poll
    # polls = list(set([answer.poll for answer in answers]))
    # ## format the information got in answers accordingly
    # for poll in polls:
    #     item = {
    #             "title": poll.title,
    #             "id": poll.id,
    #             "answers": []
    #     }
    #     for answer in answers:
    #         if answer.poll.title == poll.title:
    #             answerObj = {
    #                 "value": answer.value,
    #                 "user_first_name": answer.user.first_name,
    #                 "user_last_name": answer.user.last_name,
    #                 "id": answer.user.id
    #             }
    #             item['answers'].append(answerObj)
    #     context["polls"].append(item)
    
    
    polls = models.Poll.objects.all()
    for poll in polls:

        item = {
            "title": poll.title,
            "id": poll.pk,
            "answers": [{
                "value": answer.value,
                "user_first_name": answer.user.first_name,
                "user_last_name": answer.user.last_name,
                "id": answer.pk,
            } for answer in poll.answers.all().select_related('user')] #bad query spotted, improved by adding a 'join' to user table
        }
        context['polls'].append(item)

    return render(request, 'polls/index.html', context)

@login_required
def my_profile(request):
    current_user_profile = request.user.profile
    user_form = models.ProfileForm.objects.get(site=current_user_profile.site) #query
    fields = user_form.form_fields['fields']
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    data.update(current_user_profile.dynamic_fields)
    form = ProfileForm(fields=fields, initial=data)
    return render(request, 'polls/current_user.html', {'form': form})

@login_required
@csrf_exempt
def edit_answer(request, poll_id, answer_id):
    payload = json.loads(request.body)
    answer = models.Answer.objects.get(pk=answer_id) #query
    answer.value = payload.get('value')
    answer.save()
    return JsonResponse({"value": answer.value})