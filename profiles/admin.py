from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import (
    ModelForm,
    ModelMultipleChoiceField
)
from django.utils.translation import gettext_lazy as _

from core.models import (
    Component
)
from profiles.models import (
    TutorProfile,
    StudentProfile,
    ParentProfile,
    Education,
    TutorQualification,
    SubjectOffered,
)


class TutorProfileAdminForm(ModelForm):
    class Meta:
        model = TutorProfile
        exclude = []

    features = ModelMultipleChoiceField(
        queryset=Component.objects.filter(componentGroup__code='TUTOR_FEATURE'),
        required=False,
        label=_('Features'),
        widget=FilteredSelectMultiple(
            verbose_name=_('Features'),
            is_stacked=False
        )
    )
    clearanceLevels = ModelMultipleChoiceField(
        queryset=Component.objects.filter(componentGroup__code='CLEARANCE'),
        required=False,
        label=_('Clearance Levels'),
        widget=FilteredSelectMultiple(
            verbose_name=_('Clearance Levels'),
            is_stacked=False
        )
    )


class TutorProfileAdmin(admin.ModelAdmin):
    form = TutorProfileAdminForm


admin.site.register(TutorProfile, TutorProfileAdmin)
admin.site.register(StudentProfile)
admin.site.register(ParentProfile)
admin.site.register(Education)
admin.site.register(TutorQualification)
admin.site.register(SubjectOffered)
