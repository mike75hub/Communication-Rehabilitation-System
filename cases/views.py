from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Case, RehabilitationPlan, PlanItem
from .forms import CaseForm, RehabilitationPlanForm, PlanItemForm

@login_required
def case_list(request):
    cases = Case.objects.all()
    return render(request, 'cases/case_list.html', {'cases': cases})

@login_required
def case_detail(request, pk):
    case = get_object_or_404(Case, pk=pk)
    rehabilitation_plans = case.rehabilitation_plans.all()
    
    context = {
        'case': case,
        'rehabilitation_plans': rehabilitation_plans
    }
    return render(request, 'cases/case_detail.html', context)

@login_required
def case_create(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save()
            messages.success(request, f'Case for {case.client.full_name} created successfully!')
            return redirect('case_detail', pk=case.pk)
    else:
        form = CaseForm(initial={'officer': request.user})
    
    return render(request, 'cases/case_form.html', {'form': form, 'title': 'Create Case'})

@login_required
def rehabilitation_plan_create(request, case_pk):
    case = get_object_or_404(Case, pk=case_pk)
    
    if request.method == 'POST':
        form = RehabilitationPlanForm(request.POST)
        if form.is_valid():
            rehabilitation_plan = form.save(commit=False)
            rehabilitation_plan.case = case
            rehabilitation_plan.save()
            messages.success(request, 'Rehabilitation plan created successfully!')
            return redirect('case_detail', pk=case_pk)
    else:
        form = RehabilitationPlanForm()
    
    return render(request, 'cases/rehabilitation_plan_form.html', {
        'form': form,
        'case': case,
        'title': 'Add Rehabilitation Plan'
    })