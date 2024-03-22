from setuptools import setup, find_packages

setup(
    name='talkingclock',
    version='0.5',
    packages=find_packages(where="src"),
    include_package_data=True,
    package_dir={"":"src"}, 
    package_data={
        'talkingclock': ["mp3/*.mp3"],
    },
    install_requires=[
        'playsound',
    ],
)
