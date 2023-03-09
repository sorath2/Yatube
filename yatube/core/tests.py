from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_page_404(self):
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
