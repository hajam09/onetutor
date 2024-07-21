from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


class Profile:

    def __init__(self, name, description, icon, url):
        self.name = name
        self.description = description
        self.icon = icon
        self.url = url


def getProfileSelectComponent(profile: Profile):
    itemContent = f'''
    <div class="col-lg-4 col-md-4 col-sm-10 pb-4 d-block m-auto">
        <div class="pricing-item" style="box-shadow: 0px 0px 30px -7px rgba(0,0,0,0.29);">
            <div class="pt-4 pb-3" style="letter-spacing: 2px">
                <h4>{profile.name}</h4>
            </div>
            <div class="pricing-price pb-1 text-primary color-primary-text ">
                <img src="{profile.icon}"
                     height="143" width="137">
            </div>
            <div class="pricing-description">
                <ul class="list-unstyled mt-3 mb-4">
                    <li class="pl-3 pr-3">{profile.description}
                    </li>
                </ul>
            </div>
            <div class="pricing-button pb-4">
                <a href="{profile.url}" type="button"
                   class="btn btn-lg btn-primary w-75">Select</a>
            </div>
        </div>
    </div>
    '''
    return mark_safe(itemContent)


@register.simple_tag
def render():
    # TODO: Find better icons for all profiles and upload them to common cdn.
    profiles = [
        Profile(
            "Student",
            "Get taught by verified tutors, review study materials or chat with a tutor.",
            "https://thumbs.dreamstime.com/b/cartoon-black-man-student-talking-cartoon-illustration-black-man-student-talking-116196595.jpg",
            f"{reverse('accounts:create-profile') + '?type=student'}",
        ),
        Profile(
            "Parent",
            "Parents account to manage their children's activities and for consent.",
            "https://us.123rf.com/450wm/yupiramos/yupiramos1904/yupiramos190418715/123390809-young-couple-avatars-characters-vector-illustration-design.jpg?ver=6",
            f"{reverse('accounts:create-profile') + '?type=parent'}",
        ),
        Profile(
            "Tutor",
            "Tutor the students and manage lessons with your students.",
            "https://www.pngitem.com/pimgs/m/81-814137_teacher-education-student-teacher-cartoon-teacher-transparent-background.png",
            f"{reverse('accounts:create-profile') + '?type=tutor'}",
        )
    ]
    itemContent = f'''
        <br>
        <h2 class="text-center">Select the profile you want to create.</h2>
        <br><br><br>
        <div class="container text-center">
            <div class="row">
                {"".join([getProfileSelectComponent(profile) for profile in profiles])}
            </div>
        </div>
    '''
    return mark_safe(itemContent)
