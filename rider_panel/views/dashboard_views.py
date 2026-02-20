from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class DashboardView(LoginRequiredMixin, View):
    login_url = 'rider_panel:login'
    template_name = 'rider_panel/dashboard/home.html'

    def get(self, request):
        if request.user.role != 'RIDER':
            # Strictly only allow Riders
            from django.contrib.auth import logout
            logout(request)
            return redirect('rider_panel:login')
            
        return render(request, self.template_name)
