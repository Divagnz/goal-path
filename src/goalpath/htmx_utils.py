"""
HTMX Utilities for GoalPath
Helper functions for HTMX request detection and response handling
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Get templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=templates_dir)


def is_htmx_request(request: Request) -> bool:
    """
    Detect if the request is from HTMX by checking headers.
    HTMX sends HX-Request header with all requests.
    """
    return request.headers.get("HX-Request") == "true"


def get_htmx_trigger(request: Request) -> Optional[str]:
    """
    Get the element that triggered the HTMX request.
    """
    return request.headers.get("HX-Trigger")


def get_htmx_target(request: Request) -> Optional[str]:
    """
    Get the target element for the HTMX request.
    """
    return request.headers.get("HX-Target")


def htmx_response(
    template_name: str,
    context: Dict[str, Any],
    request: Request,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None,
    trigger: Optional[Union[str, Dict[str, Any]]] = None,
    push_url: Optional[str] = None,
    redirect: Optional[str] = None,
    refresh: bool = False,
    swap: Optional[str] = None,
    target: Optional[str] = None,
) -> HTMLResponse:
    """
    Create an HTMX-compatible HTML response with proper headers.

    Args:
        template_name: Jinja2 template to render
        context: Template context data
        request: FastAPI request object
        status_code: HTTP status code
        headers: Additional response headers
        trigger: Event to trigger on client (string or dict)
        push_url: URL to push to browser history
        redirect: URL to redirect to
        refresh: Whether to refresh the page
        swap: How to swap the content (innerHTML, outerHTML, etc.)
        target: CSS selector for where to swap content
    """
    # Render the template
    html_content = templates.get_template(template_name).render(context)

    # Prepare response headers
    response_headers = headers or {}

    # Add HTMX-specific headers
    if trigger:
        if isinstance(trigger, dict):
            import json

            response_headers["HX-Trigger"] = json.dumps(trigger)
        else:
            response_headers["HX-Trigger"] = str(trigger)

    if push_url:
        response_headers["HX-Push-Url"] = push_url

    if redirect:
        response_headers["HX-Redirect"] = redirect

    if refresh:
        response_headers["HX-Refresh"] = "true"

    if swap:
        response_headers["HX-Reswap"] = swap

    if target:
        response_headers["HX-Retarget"] = target

    return HTMLResponse(content=html_content, status_code=status_code, headers=response_headers)


def htmx_error_response(
    error_message: str,
    request: Request,
    status_code: int = 400,
    field_errors: Optional[Dict[str, str]] = None,
    trigger_close_modal: bool = False,
) -> HTMLResponse:
    """
    Create an HTMX error response with proper error handling.

    Args:
        error_message: Main error message
        request: FastAPI request object
        status_code: HTTP status code for the error
        field_errors: Dictionary of field-specific errors
        trigger_close_modal: Whether to trigger modal close
    """
    context = {
        "request": request,
        "error_message": error_message,
        "field_errors": field_errors or {},
        "status_code": status_code,
    }

    headers = {}
    if trigger_close_modal:
        headers["HX-Trigger"] = "closeModal"

    return htmx_response(
        template_name="fragments/error_message.html",
        context=context,
        request=request,
        status_code=status_code,
        headers=headers,
    )


def htmx_success_response(
    template_name: str,
    context: Dict[str, Any],
    request: Request,
    success_message: str,
    trigger_close_modal: bool = True,
    additional_triggers: Optional[Dict[str, Any]] = None,
) -> HTMLResponse:
    """
    Create an HTMX success response with notifications.

    Args:
        template_name: Template to render for the updated content
        context: Template context
        request: FastAPI request object
        success_message: Success message for notification
        trigger_close_modal: Whether to close the modal
        additional_triggers: Additional events to trigger
    """
    # Prepare trigger events
    triggers = {
        "showNotification": {"type": "success", "title": "Success", "message": success_message}
    }

    if trigger_close_modal:
        triggers["closeModal"] = True

    if additional_triggers:
        triggers.update(additional_triggers)

    return htmx_response(
        template_name=template_name, context=context, request=request, trigger=triggers
    )


def render_template(template_name: str, request: Request, **context) -> HTMLResponse:
    """
    Render a template and return as HTMLResponse.
    Convenience function for HTMX endpoints.
    """
    context["request"] = request
    html_content = templates.get_template(template_name).render(context)
    return HTMLResponse(content=html_content)


def render_fragment(template_name: str, context: Dict[str, Any], request: Request) -> str:
    """
    Render a template fragment and return as string.
    Useful for partial content updates.
    """
    context["request"] = request
    return templates.get_template(template_name).render(context)


class HTMXDepends:
    """
    FastAPI dependency for HTMX request validation.
    Use this to ensure endpoints are only called via HTMX.
    """

    def __call__(self, request: Request) -> bool:
        if not is_htmx_request(request):
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400, detail="This endpoint is only accessible via HTMX requests"
            )
        return True


# Global instance for dependency injection
htmx_required = HTMXDepends()


def get_form_data(request: Request) -> Dict[str, Any]:
    """
    Helper to extract form data from HTMX request.
    Handles both form data and JSON payloads.
    """
    # This will be used in async context, so we'll need to handle it properly
    # in the actual endpoint implementations
    pass
