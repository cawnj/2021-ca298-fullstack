from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['products', 'view_basket', 'checkout', 'login', 'logout', 'register', 'product_form', 'admin_signup']

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return timezone.now()