from collections import deque
from math import inf

from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect


services = (('change_oil', 2), ('inflate_tires', 5), ('diagnostic', 30))
line_of_cars = {service[0]: deque() for service in services}


def minutes_to_wait(service):
    for i, (service_keyword, _) in enumerate(services):
        if service_keyword == service:
            index = i
            break
    else:
        return inf

    return sum(len(line_of_cars[services[i][0]]) * services[i][1] for i in range(index + 1))


def ticket_number():
    return ProcessingView.processed + sum(len(line_of_cars[service[0]]) for service in services) + 1


def get_ticket(service):
    number = ticket_number()
    line_of_cars[service].appendleft(number)
    return number


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'tickets/menu.html')


class NextView(View):
    def get(self, request, *args, **kwargs):
        if ProcessingView.next_ticket:
            return HttpResponse(f'<div>Next ticket #{ProcessingView.next_ticket}</div>')
        else:
            return HttpResponse("<div>Waiting for the next client</div>")


class TicketView(View):
    def get(self, request, *args, **kwargs):
        service = kwargs['service']
        waiting_time = minutes_to_wait(service)
        return HttpResponse(f"""<div>Your numbre is {get_ticket(service)}</div>
                                <div>Please wait around {waiting_time} minutes</div>""")


class ProcessingView(View):
    processed = 0
    next_ticket = 0

    @classmethod
    def next(cls):
        for line, cars in line_of_cars.items():
            if len(cars) != 0:
                cls.next_ticket = cars.pop()
                cls.processed += 1
                break
        else:
            cls.next_ticket = 0
            cls.processed = 0

    def get(self, request, *args, **kwargs):
        lines = ['Change oil', 'Inflate tires', 'Get diagnostic']
        lengths = [len(cars) for cars in [*line_of_cars.values()]]
        length_of_lines = {lines[i]: lengths[i] for i in range(len(lines))}
        return render(request, "tickets/processing.html", context={'length_of_lines': length_of_lines})

    def post(self, request, *args, **kwargs):
        self.next()
        return redirect("/next")
