import os
import random
import string
import time

import pyautogui
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


def generate_username() -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(random.randint(4, 20)))


def generate_password() -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(random.randint(6, 40)))


def generate_email() -> str:
    return generate_username() + "@yandex.ru"


def test_login(driver):
    driver.get("http://localhost:3000/login")

    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    username.send_keys("gelo121region")
    password.send_keys("string1")

    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
    login_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/home" in driver.current_url


def test_failed_login(driver):
    driver.get("http://localhost:3000/login")

    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    username.send_keys("wrong_username")
    password.send_keys("wrong_password")

    login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Войти')]")
    login_button.click()

    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:3000/login"))
    time.sleep(2)
    error_message = driver.find_element(By.XPATH,
                                        '//div[@class="css-1v0ca7"]/p')
    assert error_message.is_displayed()


def test_registration(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    time.sleep(2)

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    email.send_keys(generate_email())
    username.send_keys(generate_username())
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()
    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url


def test_failed_registration(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")

    email.send_keys('user@example.com')
    username.send_keys(generate_username())
    password.send_keys(generate_password())

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_button.click()

    time.sleep(2)
    error_message = driver.find_element(By.XPATH,
                                        "//p[contains(text(), 'Пользователь с таким email существует.')]")
    assert error_message.is_displayed()


def test_form_validation(driver):
    driver.get("http://localhost:3000/registration")

    registration_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    assert registration_button.get_attribute('disabled') is not None

    email = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "uname")))
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "psw")))

    email.send_keys("emailTest1@email.com")
    username.send_keys("test1")
    password.send_keys("123")

    password_error_message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                               "//p[contains(text(), 'Пароль должен содержать от 6 до 40 символов и может включать буквы, цифры и спец символы.')]")))
    assert password_error_message.is_displayed()
    assert registration_button.get_attribute('disabled') is not None

    clearButton = driver.find_element(By.XPATH, "//button[contains(text(), 'Очистить')]")
    clearButton.click()

    password.send_keys("123aaa")
    email.send_keys("emailTest1@email.com")
    username.send_keys("test")

    login_error_message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                            "//p[contains(text(), 'Имя пользователя должно содержать от 4 до 20 символов и должно включать буквы и цифры.')]")))
    assert login_error_message.is_displayed();
    assert registration_button.get_attribute('disabled') is not None

    clearButton.click()

    password.send_keys("123aaa")
    username.send_keys("test1")
    email.send_keys("emailInvalid")

    login_error_message = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH,
                                                                                            "//p[contains(text(), 'Некорректный формат email')]")))
    assert login_error_message.is_displayed();
    assert registration_button.get_attribute('disabled') is not None


def test_cleaning(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")

    email.send_keys("testusexr123@yandex.com")
    username.send_keys("yellow")
    password.send_keys("string1")

    clear_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Очистить')]")
    clear_button.click()

    assert email.text == ""
    assert username.text == ""
    assert password.text == ""


def test_favorites(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    time.sleep(2)

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    email.send_keys(generate_email())
    username.send_keys(generate_username())
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url

    room_name: str = generate_username()

    room_name_input = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div/div[2]/div[1]/input")
    room_name_input.send_keys(room_name)

    driver.find_element(By.XPATH, "//button[contains(text(), 'Создать комнату')]").click()

    time.sleep(2)
    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f"http://localhost:3000/dashboard/{room_name}" in driver.current_url

    driver.find_element(By.XPATH, "//a[contains(text(), 'Закладки')]").click()

    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:3000/favorites"))
    assert "http://localhost:3000/favorites" in driver.current_url
    time.sleep(2)

    favorite_rooms = driver.find_elements(By.CSS_SELECTOR, ".MuiChip-root.MuiChip-clickable.MuiChip-deletable")

    assert len(favorite_rooms) > 0

    driver.find_element(By.XPATH, "//a[contains(text(), 'Выйти из системы')]").click()
    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:3000/login"))
    assert "http://localhost:3000/login" in driver.current_url


def test_favorites_2(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url
    time.sleep(5)

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    email.send_keys(generate_email())
    username.send_keys(generate_username())
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url
    time.sleep(2)
    # нажимать на кнопку добавления в закладки
    favorite_rooms = driver.find_elements(By.CSS_SELECTOR, ".MuiSvgIcon-root.MuiChip-deleteIcon")

    for favorite_room in favorite_rooms:
        favorite_room.click()

    driver.find_element(By.XPATH, "//a[contains(text(), 'Закладки')]").click()

    WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:3000/favorites"))
    assert "http://localhost:3000/favorites" in driver.current_url
    time.sleep(2)
    # посмотреть что они тут есть.
    favorite_rooms = driver.find_elements(By.CSS_SELECTOR, ".MuiChip-root.MuiChip-clickable.MuiChip-deletable")

    favorite_rooms_count = len(favorite_rooms)

    assert favorite_rooms_count > 0

    favorite_room = driver.find_element(By.CSS_SELECTOR, ".MuiSvgIcon-root.MuiChip-deleteIcon")
    favorite_room.click()

    driver.refresh()
    time.sleep(2)

    prev_favorite_rooms_count = favorite_rooms_count
    favorite_rooms = driver.find_elements(By.CSS_SELECTOR, ".MuiChip-root.MuiChip-clickable.MuiChip-deletable")

    assert len(favorite_rooms) == prev_favorite_rooms_count - 1


def test_chat_text_message(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    time.sleep(5)

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    username_str = generate_username()
    email.send_keys(generate_email())
    username.send_keys(username_str)
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url

    room_name_str = generate_username()
    room_name = driver.find_element(By.XPATH, "//div[@class='css-96r7gq']//input[@id='messageText']")
    room_name.send_keys(room_name_str)

    create_room_button = driver.find_element(By.XPATH, "//button[@class='css-1hy3zlq']")
    create_room_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url

    time.sleep(1)
    message_str = "1234lox"
    message_field = driver.find_element(By.XPATH, "//input[@id='messageText']")
    message_field.send_keys(message_str)

    message_send_button = driver.find_element(By.XPATH, "//button[@class='css-17iq27n']")
    message_send_button.click()
    time.sleep(1)

    home_button = driver.find_element(By.XPATH, "//a[contains(text(),'Домашняя страница')]")
    home_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/home" in driver.current_url
    time.sleep(2)

    room_buttom = driver.find_element(By.XPATH, f"//div[@id='{room_name_str}']")
    room_buttom.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url
    time.sleep(1)

    user_in_list = driver.find_element(By.XPATH, f"//*[contains(text(), '{username_str}')]")
    assert user_in_list.is_displayed()
    message_in_history = driver.find_element(By.XPATH, "//*[contains(text(), '1234lox')]")
    assert message_in_history.is_displayed()
    time.sleep(1)

    logout_button = driver.find_element(By.XPATH, "//a[contains(text(),'Выйти из системы')]")
    logout_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/login" in driver.current_url


def test_chat_media_file(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    time.sleep(2)

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    username_str = generate_username()
    email.send_keys(generate_email())
    username.send_keys(username_str)
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url

    room_name_str = generate_username()
    room_name = driver.find_element(By.XPATH, "//div[@class='css-96r7gq']//input[@id='messageText']")
    room_name.send_keys(room_name_str)

    create_room_button = driver.find_element(By.XPATH, "//button[@class='css-1hy3zlq']")
    create_room_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url
    time.sleep(1)

    upload_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../resources/", "selenium_mediafile.png"))
    media_file_attach = driver.find_element(By.XPATH, "//button[@class='css-p14d8s']")
    media_file_attach.click()
    time.sleep(1)

    pyautogui.write(upload_file)
    pyautogui.press('enter')
    time.sleep(1)

    message_send_button = driver.find_element(By.XPATH, "//button[@class='css-17iq27n']")
    message_send_button.click()
    time.sleep(5)

    home_button = driver.find_element(By.XPATH, "//a[contains(text(),'Домашняя страница')]")
    home_button.click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/home" in driver.current_url
    time.sleep(1)

    room_buttom = driver.find_element(By.XPATH, f"//div[@id='{room_name_str}']")
    room_buttom.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url
    time.sleep(1)

    user_in_list = driver.find_element(By.XPATH, f"//*[contains(text(), '{username_str}')]")
    assert user_in_list.is_displayed()
    media_in_history = driver.find_element(By.XPATH, "//img[@alt='uploaded file']")
    assert media_in_history.is_displayed()
    time.sleep(1)

    logout_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Выйти из системы')]")
    logout_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/login" in driver.current_url


def test_chat_text_message_and_media_file(driver):
    driver.get("http://localhost:3000/login")

    register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Регистрация')]")
    register_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/login"))
    assert "http://localhost:3000/registration" in driver.current_url

    email = driver.find_element(By.NAME, "email")
    username = driver.find_element(By.NAME, "uname")
    password = driver.find_element(By.NAME, "psw")
    username_str = generate_username()
    email.send_keys(generate_email())
    username.send_keys(username_str)
    password.send_keys(generate_password())

    register_submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Зарегистрироваться')]")
    register_submit_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/registration"))
    assert "http://localhost:3000/home" in driver.current_url

    room_name_str = generate_username()
    room_name = driver.find_element(By.XPATH, "//div[@class='css-96r7gq']//input[@id='messageText']")
    room_name.send_keys(room_name_str)

    create_room_button = driver.find_element(By.XPATH, "//button[@class='css-1hy3zlq']")
    create_room_button.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url
    time.sleep(1)

    message_str = "4321xol"
    message_field = driver.find_element(By.XPATH, "//input[@id='messageText']")
    message_field.send_keys(message_str)
    time.sleep(1)

    upload_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../..", "selenium_mediafile.png"))
    media_file_attach = driver.find_element(By.XPATH, "//button[@class='css-p14d8s']")
    media_file_attach.click()
    time.sleep(1)

    pyautogui.write(upload_file)
    pyautogui.press('enter')
    time.sleep(1)

    message_send_button = driver.find_element(By.XPATH, "//button[@class='css-17iq27n']")
    message_send_button.click()
    time.sleep(5)

    home_button = driver.find_element(By.XPATH, "//a[contains(text(),'Домашняя страница')]")
    home_button.click()
    time.sleep(1)

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/home" in driver.current_url
    time.sleep(1)

    room_buttom = driver.find_element(By.XPATH, f"//div[@id='{room_name_str}']")
    room_buttom.click()

    WebDriverWait(driver, 10).until(EC.url_changes("http://localhost:3000/home"))
    assert f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}' in driver.current_url
    time.sleep(1)

    user_in_list = driver.find_element(By.XPATH, f"//*[contains(text(), '{username_str}')]")
    assert user_in_list.is_displayed()
    media_in_history = driver.find_element(By.XPATH, "//img[@alt='uploaded file']")
    assert media_in_history.is_displayed()
    time.sleep(1)

    logout_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Выйти из системы')]")
    logout_button.click()

    WebDriverWait(driver, 10).until(
        EC.url_changes(f'http://localhost:3000/dashboard/{room_name_str.replace(" ", "%20")}'))
    assert "http://localhost:3000/login" in driver.current_url
