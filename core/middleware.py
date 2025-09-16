import logging
import time
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

logger = logging.getLogger('security')
User = get_user_model()


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Only add security headers in production
        if not settings.DEBUG:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
            
            # Add HSTS header for HTTPS
            if request.is_secure():
                response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware for additional protection"""
    
    def process_request(self, request):
        # Skip rate limiting for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
            
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Rate limit based on IP
        cache_key = f'rate_limit_{client_ip}'
        requests = cache.get(cache_key, 0)
        
        # Allow 100 requests per minute per IP
        if requests >= 100:
            logger.warning(f'Rate limit exceeded for IP: {client_ip}')
            return HttpResponse(b'Rate limit exceeded. Please try again later.', status=429)
        
        # Increment request count
        cache.set(cache_key, requests + 1, 60)  # 1 minute timeout
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LoginAttemptMiddleware(MiddlewareMixin):
    """Monitor failed login attempts"""
    
    def process_request(self, request):
        # Only monitor login attempts
        if request.path == '/accounts/login/' and request.method == 'POST':
            client_ip = self.get_client_ip(request)
            cache_key = f'login_attempts_{client_ip}'
            attempts = cache.get(cache_key, 0)
            
            # Allow 5 login attempts per 15 minutes per IP
            if attempts >= 5:
                logger.warning(f'Excessive login attempts from IP: {client_ip}')
                return HttpResponse(b'Too many login attempts. Please try again later.', status=429)
        
        return None
    
    def process_response(self, request, response):
        # Track failed login attempts
        if (request.path == '/accounts/login/' and 
            request.method == 'POST' and 
            response.status_code == 200 and 
            'error' in str(response.content)):
            
            client_ip = self.get_client_ip(request)
            cache_key = f'login_attempts_{client_ip}'
            attempts = cache.get(cache_key, 0)
            cache.set(cache_key, attempts + 1, 900)  # 15 minutes timeout
            
            logger.warning(f'Failed login attempt from IP: {client_ip}')
        
        return response
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RequestLoggingMiddleware(MiddlewareMixin):
    """Log suspicious requests"""
    
    def process_request(self, request):
        # Log requests to sensitive endpoints
        sensitive_paths = ['/admin/', '/api/', '/accounts/']
        
        for path in sensitive_paths:
            if request.path.startswith(path):
                client_ip = self.get_client_ip(request)
                user = getattr(request, 'user', None)
                username = user.username if user and user.is_authenticated else 'Anonymous'
                
                logger.info(f'Request to {request.path} from IP: {client_ip}, User: {username}')
                break
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CSRFFailureMiddleware(MiddlewareMixin):
    """Handle CSRF failures gracefully"""
    
    def process_exception(self, request, exception):
        from django.middleware.csrf import CsrfViewMiddleware
        
        if isinstance(exception, Exception) and 'CSRF' in str(exception):
            client_ip = self.get_client_ip(request)
            logger.warning(f'CSRF failure from IP: {client_ip}, Path: {request.path}')
        
        return None
    
    def get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip