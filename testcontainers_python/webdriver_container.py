from time import sleep

from testcontainers_python import config
from testcontainers_python.brogress_bar import ConsoleProgressBar
from testcontainers_python.docker_client import DockerClient
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from testcontainers_python.exceptions import TimeoutException


class WebDriverContainer(object):
    def __init__(self, capabilities=DesiredCapabilities.FIREFOX):
        self._docker = DockerClient()
        self.capabilities = capabilities
        self._driver = None
        self._containers = []

    def __enter__(self):
        return self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

    def start(self):
        """
        Start selenium containers and wait until they are ready
        :return:
        """
        self._containers.append(self._docker.run(**config.hub))
        if self.capabilities["browserName"] == "firefox":
            self._containers.append(self._docker.run(**config.firefox_node))
        else:
            self._containers.append(self._docker.run(**config.chrome_node))
        self._driver = self._wait_for_container_to_start()
        return self

    def _wait_for_container_to_start(self):
        bar = ConsoleProgressBar().bar
        for _ in bar(range(0, config.max_tries)):
            try:
                return webdriver.Remote(
                    command_executor='http://127.0.0.1:4444/wd/hub',
                    desired_capabilities=self.capabilities)
            except Exception:
                sleep(config.sleep_time)
        raise TimeoutException("Wait time exceeded {} sec.".format(config.max_tries))

    def stop(self):
        """
        Stop all spawned containers
        :return:
        """
        for cont in self._containers:
            self._docker.remove(cont, True)

    def get_driver(self):
        return self._driver
