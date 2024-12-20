from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView, PasswordChangeView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DetailView, TemplateView
from formtools.wizard.views import SessionWizardView

from .forms import UserTypeForm, TenantRegistrationForm, LandlordRegistrationForm, UpdateUserProfileForm, \
    AdditionalInfoForm, \
    UpdateUserAddressForm, UpdatePhoneNumberForm
from .models import User
from ..property_management.models import BoardingRoom, Booking


# Create your views here.
def home(request):
    total_tenants = User.objects.filter(user_type=User.Type.TENANT).count()
    total_landlords = User.objects.filter(user_type=User.Type.LANDLORD).count()
    total_rooms = BoardingRoom.objects.count()
    total_bookings = Booking.objects.count()
    total_users = total_tenants + total_landlords
    return render(request, "authentication/home.html", {
        'total_tenants': total_tenants,
        'total_landlords': total_landlords,
        'total_rooms': total_rooms,
        'total_bookings': total_bookings,
        'total_users': total_users,
    })


class ProfileView(DetailView):
    model = User
    template_name = "authentication/profile.html"
    context_object_name = "user_profile"

    def get_template_names(self):
        user_profile = self.get_object()
        if user_profile.user_type == 'tenant':
            return ["authentication/tenant/profile.html"]
        elif user_profile.user_type == 'landlord':
            return ["authentication/landlord/profile.html"]
        else:
            return ["authentication/profile.html"]

    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return get_object_or_404(User, pk=self.kwargs['pk'])
        elif 'username' in self.kwargs:
            return get_object_or_404(User, username=self.kwargs['username'])
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['address_form'] = UpdateUserAddressForm()
        context['phone_number_form'] = UpdatePhoneNumberForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()

        if 'update-user_address_form' in request.POST:
            address_form = UpdateUserAddressForm(request.POST, instance=self.request.user)
            if address_form.is_valid():
                address_form.save()
                messages.success(request, 'Address updated successfully.')
                return redirect(self.object.get_absolute_url())
            else:
                context['address_form'] = address_form
        elif 'update-user_contact_form' in request.POST:
            phone_number_form = UpdatePhoneNumberForm(request.POST, instance=self.request.user)
            if phone_number_form.is_valid():
                phone_number_form.save()
                messages.success(request, 'Phone number updated successfully.')
                return redirect(self.object.get_absolute_url())
            else:
                context['phone_number_form'] = phone_number_form
        elif 'cancel-booking' in request.POST:
            from features.property_management.models import Booking
            booking_id = request.POST.get('cancel-booking')
            booking = get_object_or_404(Booking, id=booking_id)

            # Ensure only authorized users can cancel booking
            if booking.tenant != request.user:
                return HttpResponseForbidden("You are not allowed to cancel this booking.")

            booking.status = Booking.Status.CANCELLED
            booking.save()
            messages.success(request, "Booking cancelled successfully.")
            return redirect(self.object.get_absolute_url())
        elif 'mark-read-notification' in request.POST:
            from features.notification.models import Notification
            notification_id = request.POST.get('mark-read-notification')
            notification = get_object_or_404(Notification, id=notification_id)

            # Ensure only authorized users can mark notification as read
            if notification.user != request.user:
                return HttpResponseForbidden("You are not allowed to mark this notification as read.")

            notification.is_read = True
            notification.save()
            messages.success(request, "Notification marked as read.")
            return HttpResponseRedirect(f"{self.object.get_absolute_url()}?tab=notifications")
        elif 'delete-notification' in request.POST:
            from features.notification.models import Notification
            notification_id = request.POST.get('delete-notification')
            notification = get_object_or_404(Notification, id=notification_id)

            # Ensure only authorized users can delete notification
            if notification.user != request.user:
                return HttpResponseForbidden("You are not allowed to delete this notification.")

            notification.delete()
            messages.success(request, "Notification deleted.")
            return HttpResponseRedirect(f"{self.object.get_absolute_url()}?tab=notifications")

        return self.render_to_response(context)


class ChangePasswordView(PasswordChangeView):
    template_name = "authentication/change_password.html"
    success_url = reverse_lazy('authentication:my-profile')


class UpdateProfileView(UpdateView):
    model = User
    form_class = UpdateUserProfileForm
    template_name = "authentication/edit_profile.html"
    success_url = reverse_lazy('authentication:my-profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


# TODO: Restrict access to this view to users who have not yet filled out their additional info
class AdditionalInfoView(UpdateView):
    model = User
    form_class = AdditionalInfoForm
    template_name = "authentication/additional_info.html"
    success_url = reverse_lazy('authentication:home')

    def get_object(self, queryset=None):
        return self.request.user


class LogoutView(DjangoLogoutView):
    template_name = "authentication/logout.html"


class LoginView(DjangoLoginView):
    template_name = "authentication/login.html"


class RegistrationWizard(SessionWizardView):
    TEMPLATES = {
        "user_type": "authentication/user_type_form.html",
        "tenant_registration": "authentication/tenant_registration_form.html",
        "landlord_registration": "authentication/landlord_registration_form.html",
    }

    form_list = [
        ("user_type", UserTypeForm),
        ("tenant_registration", TenantRegistrationForm),
        ("landlord_registration", LandlordRegistrationForm),
    ]

    condition_dict = {
        "tenant_registration": lambda self: self.is_tenant(),
        "landlord_registration": lambda self: self.is_landlord(),
    }

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def is_tenant(self):
        user_type = self.get_cleaned_data_for_step('user_type')
        return user_type and user_type.get('user_type') == 'tenant'

    def is_landlord(self):
        user_type = self.get_cleaned_data_for_step('user_type')
        return user_type and user_type.get('user_type') == 'landlord'

    def done(self, form_list, **kwargs):
        for form in form_list:
            if hasattr(form, 'save') and form.cleaned_data:
                form.save()

        # return render(self.request, 'authentication/registration_done.html', {
        #     'form_data': [forms.cleaned_data for forms in form_list if forms.cleaned_data],
        # })
        return redirect('authentication:personal-information')


class EditProfileView(TemplateView):
    template_name = 'authentication/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UpdateUserProfileForm(instance=self.request.user)
        context['address_form'] = UpdateUserAddressForm()
        context['phone_number_form'] = UpdatePhoneNumberForm()
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        if 'update-user_profile_form' in request.POST:
            profile_form = UpdateUserProfileForm(request.POST, request.FILES, instance=self.request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('authentication:edit-profile')
            else:
                context['profile_form'] = profile_form
        elif 'update-user_address_form' in request.POST:
            address_form = UpdateUserAddressForm(request.POST, instance=self.request.user)
            if address_form.is_valid():
                address_form.save()
                messages.success(request, 'Address updated successfully.')
                return redirect('authentication:edit-profile')
            else:
                context['address_form'] = address_form
        elif 'update-user_contact_form' in request.POST:
            phone_number_form = UpdatePhoneNumberForm(request.POST, instance=self.request.user)
            if phone_number_form.is_valid():
                phone_number_form.save()
                messages.success(request, 'Phone number updated successfully.')
                return redirect('authentication:edit-profile')
            else:
                context['phone_number_form'] = phone_number_form

        return self.render_to_response(context)
