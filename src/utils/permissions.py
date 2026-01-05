from dataclasses import dataclass


@dataclass
class Inventory:
    """
    Dataclass representing inventory-related permissions.

    Attributes:
        manage_inventory (str): Permission to manage inventory items
        view_inventory (str): Permission to view inventory items
        manage_brands (str): Permission to manage shoes
        view_brands (str): Permission to view shoes
        manage_brands (str): Permission to manage product brands
        view_brands (str): Permission to view product brands
        manage_categories (str): Permission to manage product categories
        view_categories (str): Permission to view product categories
        manage_sizes (str): Permission to manage product sizes
        view_sizes (str): Permission to view product sizes
        manage_stocks (str): Permission to manage stock levels
    """

    manage_inventory = "manage_inventory"
    view_inventory = "view_inventory"
    manage_shoes = "manage_shoes"
    view_shoes = "view_shoes"
    manage_brands = "manage_brands"
    view_brands = "view_brands"
    manage_categories = "manage_categories"
    view_categories = "view_categories"
    manage_sizes = "manage_sizes"
    view_sizes = "view_sizes"
    manage_variants = "manage_variants"
    view_variants = "view_variants"
    manage_stocks = "manage_stocks"


@dataclass
class Users:
    """
    Dataclass representing user management permissions.

    Attributes:
        manage_users (str): Permission to manage user accounts
        view_users (str): Permission to view user information
    """

    manage_users = "manage_users"
    view_users = "view_users"


@dataclass
class Sales:
    """
    Dataclass representing sales-related permissions.

    Attributes:
        manage_sales (str): Permission to manage sales transactions
        view_sales (str): Permission to view sales data and reports
    """

    manage_sales = "manage_sales"
    view_sales = "view_sales"


@dataclass
class POS:
    """
    Dataclass representing point-of-sale (POS) permissions.

    Attributes:
        use_pos (str): Permission to use the POS system
        print_receipts (str): Permission to print sales receipts
    """

    use_pos = "use_pos"
    print_receipts = "print_receipts"


@dataclass
class Management:
    """
    Dataclass representing system management permissions.

    Attributes:
        manage_roles (str): Permission to manage user roles
        manage_role_permissions (str): Permission to manage role permissions
        request_reports (str): Permission to request system reports
        admin_all (str): Administrator permissions
    """

    manage_roles = "manage_roles"
    manage_role_permissions = "manage_roles_permissions"
    request_reports = "request_reports"
    admin_all = "admin_all"


class PermissionsClass:
    """
    Dataclass representing all permission categories in the system.

    This class aggregates all permission categories including inventory, sales,
    user management, POS, and system management permissions.

    Attributes:
        inventory (Inventory): Inventory-related permissions
        sales (Sales): Sales-related permissions
        users (Users): User management permissions
        pos (POS): Point-of-sale permissions
        management (Management): System management permissions
    """
    inventory: Inventory = Inventory()
    sales: Sales = Sales()
    users: Users = Users()
    pos: POS = POS()
    management: Management = Management()


@dataclass
class PermissionCategory:
    Inventory: str = "Inventory"
    Sales: str = "Sales"
    Users: str = "Users"
    POS: str = "POS"
    Management: str = "Management"


Permissions = PermissionsClass()
