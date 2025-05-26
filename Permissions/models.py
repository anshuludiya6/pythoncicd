from django.db import models


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Role' 


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Category'

class Subcategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    subcategory_name = models.CharField(max_length=100)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'Subcategory'


class RoleCategoryPermission(models.Model):
    admin_category_permission_id = models.AutoField(primary_key=True)
    role_id = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')
    subcategory_id = models.ForeignKey(Subcategory, on_delete=models.CASCADE, null=True, db_column='subcategory_id')
    can_view = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_add = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'RoleCategoryPermission'