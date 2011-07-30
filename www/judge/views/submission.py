# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from djangoutils import setup_paginator, get_or_none
from django.contrib.auth.models import User
from ..models import Problem, Submission

@login_required
def mine(request):
    return redirect(reverse("judge-submission-recent"))

def accepted(request, problem, order_by="length", page=1):
    problem = get_object_or_404(Problem, slug=problem)
    submissions = Submission.objects.filter(state=Submission.ACCEPTED,
                                            problem=problem).order_by(order_by)
    return render(request, "submission/accepted.html",
                  {"problem": problem,
                   "order_by": order_by,
                   "pagination": setup_paginator(submissions, page,
                                                 "judge-submission-accepted",
                                                 {"problem": problem.slug,
                                                  "order_by": order_by})})

def recent(request, page=1):
    # TODO: hide non-public submission
    # TODO: handle non-public submissions in general
    submissions = Submission.objects.all().order_by("-id")

    filters = {}

    empty_message = u"제출된 답안이 없습니다."
    title_add = []

    if request.GET.get("problem"):
        slug = request.GET["problem"]
        problem = get_or_none(Problem, slug=slug)

        if not problem:
            empty_message = u"해당 문제가 없습니다."
            submissions = submissions.none()
        else:
            submissions = submissions.filter(problem=problem)

        title_add.append(slug)
        filters["problem"] = slug

    if "state" in request.GET:
        state = request.GET["state"]
        submissions = submissions.filter(state=state)
        filters["state"] = state
        title_add.append(Submission.STATES_KOR[int(state)])

    if request.GET.get("user"):
        username = request.GET["user"]
        user = get_or_none(User, username=username)
        if not user:
            empty_message = u"해당 사용자가 없습니다."
            submissions = submissions.none()
        else:
            submissions = submissions.filter(user=user)
        filters["user"] = username
        title_add.append(username)

    problems = Problem.objects.filter(state=Problem.PUBLISHED).order_by("slug")
    users = User.objects.order_by("username")

    return render(request, "submission/recent.html",
                  {"title": u"답안 목록" + (": " if title_add else "") +
                   ",".join(title_add),
                   "problems": problems,
                   "users": users,
                   "filters": filters,
                   "empty_message": empty_message,
                   "pagination": setup_paginator(submissions, page,
                                                 "judge-submission-recent", {}, filters)})

def details(request, id):
    submission = get_object_or_404(Submission, id=id)
    problem = submission.problem
    return render(request, "submission/details.html",
                  {"title": u"답안 보기",
                   "submission": submission,
                   "problem": problem})
