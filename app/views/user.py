#  Project : KSRTC Seat Availability Notification System
#  Filename : user.py
#  Author : thameem
#  Current modification time : Mon, 23 May 2022 at 12:05 AM India Standard Time
#  Last modified time : Mon, 23 May 2022 at 12:05 AM India Standard Time
from datetime import datetime

from beartype import beartype
from django.contrib import messages
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.shortcuts import render, redirect

from app.libs import authenticate
from app.models import NotificationModel, LocationModel, UserModel
from libs.get_services import GetServices


class User:

    @staticmethod
    @beartype
    @authenticate
    def dynamic_pages(request: WSGIRequest, page: str) -> 'HttpResponse':
        data = {'page_title': f"{request.session['user_name']} - {page.title()} | KSRTC Seat Availability Notification"}
        if page == 'add_notification':
            data['locations'] = LocationModel.get_all_locations()

        if page == 'notifications':
            data['notifications'] = NotificationModel.get_notifications(request.session['user'])

        return render(request, f'user/{page}.html', data)

    @staticmethod
    @beartype
    @authenticate
    def save_notification(request: WSGIRequest) -> 'HttpResponse':

        leaving_from = LocationModel.get_location_by_id(request.POST['leaving_from'])
        going_to = LocationModel.get_location_by_id(request.POST['going_to'])

        user = UserModel.get_user(firebase_uid=request.session['user'])

        date_of_departure = datetime.strptime(request.POST['date_of_departure'], "%Y-%m-%d")

        available_seats = GetServices.get_total_seats(request.POST['leaving_from'], request.POST['going_to'],
                                                      date_of_departure.date())

        _notification_obj = NotificationModel(
            leaving_from=leaving_from,
            going_to=going_to,
            date_of_departure=date_of_departure,
            date_of_return=datetime.strptime(request.POST['date_of_return'], "%Y-%m-%d") if request.POST[
                'date_of_return'] else None,
            user=user,
            available_seats=available_seats,
            time_interval=int(request.POST['time_interval']),
            receive_notification_up_to=datetime.strptime(request.POST['receive_notification_up_to'], "%Y-%m-%d"),
        )

        notification = NotificationModel.save_notification(_notification_obj)

        if notification:
            messages.success(request, 'The notification was successfully added.')
        else:
            messages.error(request, 'Some sort of error has occurred.')

        return redirect('/user/add_notification')

    @staticmethod
    @beartype
    def disable_notification(request: WSGIRequest, notification_id: str) -> 'HttpResponse':
        notification_obj = NotificationModel.get_notification(request.session['user'], notification_id)
        response = True
        if response is True:
            messages.success(request, f'notification with id {notification_id} successfully disabled')
        else:
            messages.error(request, 'Some sort of error has occurred.')

        return redirect('/user/notifications/')

    @staticmethod
    @beartype
    def update_seats(request: WSGIRequest, notification_id: str) -> 'HttpResponse':
        response = True
        if response is True:
            messages.success(request, f'notification with id {notification_id} updated successfully')
        else:
            messages.error(request, 'Some sort of error has occurred.')

        return redirect('/user/notifications/')
