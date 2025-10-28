from django.shortcuts import render

from horilla.decorators import login_required
from horilla_widgets.widgets.select_widgets import (
    ALL_INSTANCES,
    HorillaMultiSelectWidget,
)

# Create your views here.

# urls.py
# path("employee-widget-filter",views.widget_filter,name="employee-widget-filter")

# views.py
# @login_required
# def widget_filter(request):
#     """
#     This method is used to return all the ids of the employees
#     """
#     ids = EmployeeFilter(request.GET).qs.values_list("id", flat=True)
#     return JsonResponse({'ids':list(ids)})


@login_required
def get_filter_form(request):
    """
    This method will return filtering from
    """
    user_id = str(request.user.id)
    
    # Check if widget instance exists for this user
    if user_id not in ALL_INSTANCES:
        # Widget instance not found - this can happen if the view is called
        # before the widget has been rendered. Return empty content or error.
        from django.http import HttpResponse
        return HttpResponse('<div class="alert alert-warning">Widget not initialized. Please refresh the page.</div>')
    
    widget_instance = ALL_INSTANCES[user_id]
    template_path = request.GET.get("template_path")
    
    if not template_path:
        from django.http import HttpResponse
        return HttpResponse('<div class="alert alert-error">Template path not provided.</div>')
    
    # Initialize the filter class
    if widget_instance.filter_class:
        filter_instance = widget_instance.filter_class()
    else:
        from django.http import HttpResponse
        return HttpResponse('<div class="alert alert-error">Filter class not found.</div>')
    
    return render(request, template_path, {"f": filter_instance})
