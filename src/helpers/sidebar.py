
from fastapi import Request

from ..depedencies import user_permissions
from ..utils import Permissions


def check_user_permissions(user_permissions: list[str], *permissions: str):

    if Permissions.management.admin_all in user_permissions:
        return True

    for permission in permissions:
        if permission in user_permissions:
            return True

    return False


async def generate_sidebar_data(request: Request, category: str, prefix: str = "/manage"):

    navigations = {
        "Inventory": [
            {
                "href": f"{prefix}/inventory/shoes",
                "caption": "Shoes",
                "icon": "fa-shoe-prints",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.inventory.view_inventory,
                    Permissions.inventory.view_shoes,
                    Permissions.inventory.manage_shoes
                ]
            },
            {
                "href": f"{prefix}/inventory/variants",
                "caption": "Variants",
                "icon": "fa-cubes-stacked",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.inventory.view_inventory,
                    Permissions.inventory.view_variants,
                    Permissions.inventory.manage_variants
                ]
            },
            {
                "href": f"{prefix}/inventory/brands",
                "caption": "Brands",
                "icon": "fa-tag",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.inventory.view_inventory,
                    Permissions.inventory.view_brands,
                    Permissions.inventory.manage_brands
                ]
            },
            {
                "href": f"{prefix}/inventory/sizes",
                "caption": "Sizes",
                "icon": "fa-ruler",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.inventory.view_inventory,
                    Permissions.inventory.view_sizes,
                    Permissions.inventory.manage_sizes
                ]
            },
            {
                "href": f"{prefix}/inventory/categories",
                "caption": "Categories",
                "icon": "fa-rectangle-list",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.inventory.view_inventory,
                    Permissions.inventory.view_categories,
                    Permissions.inventory.manage_categories
                ]
            },
        ],
        "Sales": [
            {
                "href": f"{prefix}/sales/",
                "caption": "Sales",
                "icon": "fa-arrow-trend-up",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.sales.manage_sales,
                    Permissions.sales.view_sales
                ]
            },
            {
                "href": f"{prefix}/returns/",
                "caption": "Returns",
                "icon": "fa-right-left",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.inventory.manage_inventory,
                    Permissions.sales.manage_sales,
                    Permissions.sales.view_sales
                ]
            },
        ],
        "Management": [
            {
                "href": f"{prefix}/users/",
                "caption": "Users",
                "icon": "fa-users",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.users.manage_users,
                    Permissions.users.view_users
                ]
            },
            {
                "href": f"{prefix}/roles/",
                "caption": "Roles",
                "icon": "fa-user-group",
                "permissions": [
                    Permissions.management.admin_all,
                    Permissions.management.manage_roles,
                    Permissions.management.manage_role_permissions
                ]
            },
        ]
    }

    sidebar = []
    user_perms = await user_permissions(request)
    for item in navigations[category]:

        if check_user_permissions(user_perms, *item["permissions"]):
            sidebar.append(item)

    return sidebar
