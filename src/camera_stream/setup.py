from setuptools import find_packages, setup

package_name = 'camera_stream'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='isaac-sim',
    maintainer_email='isaac-sim@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [  'camera_stream_face = camera_stream.face_detection:main', 
        'Servo_face= camera_stream.Servo_face:main',
        'Neck_con = camera_stream.Neck_con:main'
        ],
    },
)
