"""
horilla_automations/views/ajax_views.py

AJAX views for dynamic loading of form data
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from horilla.decorators import login_required
from horilla_automations.models import MODEL_CHOICES


@login_required
@require_http_methods(["GET"])
def get_model_choices(request):
    """
    Get available model choices for the automation form
    """
    try:
        from django.apps import apps
        
        # Initialize choices
        choices = []
        
        # Add basic choices
        choices.extend([
            {"value": "employee.models.Employee", "text": "Employee"},
            {"value": "pms.models.EmployeeKeyResult", "text": "Employee Key Results"},
        ])
        
        # Try to add more from MODEL_CHOICES if available
        if MODEL_CHOICES:
            for choice_tuple in MODEL_CHOICES:
                if len(choice_tuple) >= 2:
                    choices.append({
                        "value": choice_tuple[0],
                        "text": choice_tuple[1]
                    })
        else:
            # Fallback: try to populate some basic models
            try:
                installed_apps = apps.get_app_configs()
                
                if any(app.name == 'recruitment' for app in installed_apps):
                    choices.append({
                        "value": "recruitment.models.Candidate",
                        "text": "Candidate"
                    })
                
                if any(app.name == 'leave' for app in installed_apps):
                    choices.append({
                        "value": "leave.models.LeaveRequest",
                        "text": "Leave Request"
                    })
                
                if any(app.name == 'attendance' for app in installed_apps):
                    choices.append({
                        "value": "attendance.models.Attendance",
                        "text": "Attendance"
                    })
                    
            except Exception as e:
                print(f"Error getting fallback choices: {e}")
        
        # Remove duplicates
        unique_choices = []
        seen_values = set()
        for choice in choices:
            if choice["value"] not in seen_values:
                unique_choices.append(choice)
                seen_values.add(choice["value"])
        
        return JsonResponse({
            "success": True,
            "choices": unique_choices
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e),
            "choices": [
                {"value": "employee.models.Employee", "text": "Employee"},
                {"value": "pms.models.EmployeeKeyResult", "text": "Employee Key Results"},
            ]
        })