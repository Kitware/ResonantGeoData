from setuptools import setup

setup(
    name='resonantgeodata',
    version='0.1',
    python_requires='>=3.8.0',
    install_requires=[
        'celery',
        'django',
        'django-admin-display',
        'django-allauth',
        'django-cleanup',
        'django-composed-configuration',
        'django-configurations[database,email]',
        'django-cors-headers',
        'django-crispy-forms',
        'django-extensions',
        'django-girders',
        'django-filter',
        'django-model-utils',
        'django-s3-file-field>=0.0.14',
        'djangorestframework',
        'djproxy',
        'docker',
        'drf-yasg2',
        'gputil',
        'psycopg2',
        'python-magic',
        'rich',
        'rules',
        'uritemplate',
        'whitenoise[brotli]',
        # Production-only
        'django-storages[boto3]',
        'flower',
        'gunicorn',
        'sentry-sdk',
        # Development-only
        'django-debug-toolbar',
        'django-minio-storage',
        # GeoData
        'GDAL',
        'numpy',
    ],
    extras_require={
        'dev': ['ipython', 'tox'],
        'worker': [
            'rasterio',
            'fiona',
            'shapely',
            'scipy',
            'kwarray>=0.5.10',
            'kwcoco',
            'kwimage>=0.6.7',
        ],
    },
)
