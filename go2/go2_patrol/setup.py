from glob import glob
from setuptools import setup

setup(
    name="go2_patrol",
    version="0.1.0",
    packages=["go2_patrol"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/go2_patrol"]),
        ("share/go2_patrol", ["package.xml"]),
        ("share/go2_patrol/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    entry_points={"console_scripts": [
        "record_positions = go2_patrol.record_positions:main",
        "patrol = go2_patrol.patrol:main",
        "search = go2_patrol.search:main",
    ]},
)
