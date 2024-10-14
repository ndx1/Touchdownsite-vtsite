"""Our message and conversation related views' module."""

from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from vtshop.forms import MessageForm
from vtshop.models import Conversation, Message
from vtshop.auth_utils import TestIsCustomerOrEmployeeMixin, TestIsEmployeeMixin


class MessageListView(
    LoginRequiredMixin, TestIsCustomerOrEmployeeMixin, FormMixin, ListView
):
    """Our message list view (e.g. display a conversation)."""

    login_url = "/login/"
    model = Message
    # paginate_by = 5  # if pagination is desired
    template_name = "vtshop/messages.html"
    context_object_name = "message_list"

    form_class = MessageForm

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """Check if user is a participant in conversation."""

        user = self.request.user
        conversation = get_object_or_404(Conversation, pk=self.kwargs["pk"])
        # print(conversation.participants.all())

        if user not in conversation.participants.all():
            return HttpResponse("Unauthorized", status=401)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle new message POST request."""

        form = self.form_class(request.POST)
        conversation = get_object_or_404(Conversation, pk=self.kwargs["pk"])

        if form.is_valid():
            author = self.request.user
            content = form.cleaned_data["content"]
            conversation.add_message(author=author, content=content)

        return HttpResponseRedirect(
            reverse("vtshop:messages-last", args=(conversation.id, 5))
        )

    def get_queryset(self, *args, **kwargs):
        """Message list (aka one conversation) to be displayed."""

        # n last messages to be displayed.
        if "n_last" in self.kwargs:
            n_last = int(self.kwargs["n_last"])
            m_set = list(Message.objects.filter(conversation__id=self.kwargs["pk"]))[
                -n_last:
            ]

        # all messages to be displayed.
        else:
            m_set = Message.objects.filter(conversation__id=self.kwargs["pk"])

        return m_set

    def get_context_data(self, **kwargs):
        """Related conversation and new message form to be displayed."""

        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get conversation to be displayed
        context["conversation"] = get_object_or_404(Conversation, pk=self.kwargs["pk"])

        # Form for new message
        context["form"] = self.get_form(self.form_class)

        # Only last messages or all of them
        if "n_last" in self.kwargs:
            context["n_last"] = True
        else:
            context["n_last"] = False

        return context


class ConversationListView(LoginRequiredMixin, TestIsEmployeeMixin, ListView):
    """Our conversation list view."""

    login_url = "/login/"
    model = Conversation
    # paginate_by = 5  # if pagination is desired
    template_name = "vtshop/conversations.html"
    context_object_name = "conversation_list"

    def get_queryset(self):
        """The user's conversations, with the list of participants for each."""

        user = self.request.user
        conversations = Conversation.objects.filter(participants=user).order_by(
            "date_modified"
        )

        conversation_list = []
        for conversation in conversations:
            participants = conversation.participants.all()
            conversation_list.append(
                {
                    "conversation": conversation,
                    "participants": participants,
                }
            )

        return conversation_list