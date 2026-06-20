"""
Tenant context utilities.

This module re-exports TenantContext and get_tenant_context from deps.py
to maintain backwards compatibility with modules that import from here.
"""

from app.core.deps import TenantContext, get_tenant_context, get_current_user

__all__ = ["TenantContext", "get_tenant_context", "get_current_user"]
