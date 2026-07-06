from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'hexapode'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
        data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Vyn3',
    maintainer_email='lucas.taraire@ynov.com',
    description="Commande de deplacement d'un hexapode via geometry_msgs/TwistStamped (marche tripode + IK).",
    license='MIT',
    entry_points={
        'console_scripts': [
            'ik_patte = hexapode.ik_patte:main',
            'hexapode_node = hexapode.hexapode_node:main',
        ],

    },
)
