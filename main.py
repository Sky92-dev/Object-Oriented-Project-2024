from fasthtml.common import*
from typing import List, Tuple, Optional
from datetime import datetime, time, timedelta
import copy
from uuid import uuid4
from urllib.parse import urlencode

app, rt = fast_app()
import random

# ฟังก์ชันสำหรับสุ่มสีแบบ Hex
def random_color():
    r = random.randint(180, 255)
    g = random.randint(180, 255)
    b = random.randint(180, 255)
    return f"rgb({r}, {g}, {b})"  # ใช้ RGB ที่สุ่มในช่วงที่เป็นสีอ่อน

class System:
    def __init__(self):
        self.__branches = []
        self.__menu_list = []
        self.__boxset_list = []
        self.__member_list = []
        self.__promotion_list = []
        self.__manager_list = []
        self.__delete_list = []

    def find_delete_food_by_id(self,food_id):
        for menu in self.__delete_list:
            if isinstance(menu,Food):
                if menu.get_food_id() == food_id:
                    return menu
        return None

    def find_delete_boxset_by_id(self,boxset_id):
        for boxset in self.__delete_list:
            if isinstance(boxset,Boxset):
                if boxset.get_boxset_id() == boxset_id:
                    return boxset
        return None

    def add_restore_boxset(self,boxset):
        self.__boxset_list.append(boxset)
        return "SUCCESS"

    def add_restore_food(self,food):
        self.__menu_list.append(food)
        return "SUCCESS"

    def remove_delete_list(self,menu):
        self.__delete_list.remove(menu)
        return "SUCCESS"
    
    def find_type_by_menu_id(self,menu_id):
        
        boxset = self.find_delete_boxset_by_id(menu_id)
        food = self.find_delete_food_by_id(menu_id)
        if boxset:
            return boxset
        
        elif food:
            return food
            
        return None
    

    def restore_item(self, item_id: str, manager: 'Manager'):

        item = self.find_type_by_menu_id(item_id)
        if item:
            if isinstance(item, Food):
                self.add_restore_food(item)
            elif isinstance(item, Boxset):
                self.add_restore_boxset(item)
            else:
                return "INVALID_ITEM"

            self.remove_delete_list(item)
            
            manager.add_manage_history("RESTORE", item_id)
            return Redirect("/restore_delete_menu")
        
        return "ITEM_NOT_FOUND"
    
    def delete_food_menu(self,menu):
        self.__menu_list.remove(menu)

    def delete_boxset_menu(self,boxset):
        self.__boxset_list.remove(boxset)

    def delete_item_by_id(self, item_id: str, item_type: str, manager: 'Manager'):
        if item_type == "food":
            item = self.find_food_by_id(item_id)
            if isinstance(item, Food):
                self.delete_food_menu(item)
                self.add_delete_food_menu(item)
                manager.add_manage_history("DELETE_FOOD", item_id)
                
    
        elif item_type == "boxset":
            item = self.find_boxset_by_id(item_id)
            if isinstance(item, Boxset):
                self.delete_boxset_menu(item)
                self.add_delete_boxset_menu(item)
                manager.add_manage_history("DELETE_BOXSET", item_id)
                

        return Redirect("/delete_menu")
    
                
    def find_free_rider(self,order_type):
        branch = order_type.get_branch()
        rider_in_branch = branch.get_rider()
        for rider in rider_in_branch:

            if rider.check_free() == "FREE":
                rider.set_busy()
                return rider #instance rider
        return "Busy"
        
    def add_admin(self,name,surname,tel_number,email,username,password):
        admin = Manager(name,surname,tel_number,email,username,password)
        self.__manager_list.append(admin)
    
    def add_delete_boxset_menu(self,boxset):
        self.__delete_list.append(boxset)

    def add_delete_food_menu(self,food):
        self.__delete_list.append(food)

    def find_food_by_id(self,food_id):
        for menu in self.__menu_list:
            if isinstance (menu,Food):
                if menu.get_food_id() == food_id:
                    return menu

    def find_boxset_by_id(self,boxset_id):
        for boxset in self.__boxset_list:
             if isinstance (boxset,Boxset):
                if boxset.get_boxset_id() == boxset_id:
                    return boxset
        
    def get_delete_menu(self):
        return self.__delete_list

    def add_member_list(self,account):
        self.__member_list.append(account)

    def get_menu_list(self):
        
        return self.__menu_list
    def create_account(self,name : str ,surname : str ,tel_number : str ,email : str ,username : str ,password : str):
        new_account = Member(name,surname,tel_number,email,username,password)

        self.add_member_list(new_account)
        return "CREATE ACCOUNT SUCCESS"

    def get_member_list(self):
        return self.__member_list
    
    def find_member_by_username(self,username):
        for member in self.__member_list:
            if username == member.get_username():
                return member
        for admin in self.__manager_list:
            if username == admin.get_username():
                return admin
        return "ERROR"
    
    def manage_stock(self,branch):
        member = session.get_current_user()
        basket = member.get_current_basket()
        menu_list = basket.get_item_in_basket()

        for basketitem in menu_list:
            food = basketitem.get_product()
            quantity = basketitem.get_total()
            if isinstance(food,Food):
                branch.reduce_stock(food,quantity)
        
        return "Done"
            
            
    def login(self,username,password):
        member_instance = self.find_member_by_username(username)
        if member_instance == "ERROR":
            return "FAIL"
        login_success = member_instance.verify(password)

        if login_success == "LOGIN SUCCESS":
            return "LOGIN SUCCESS"
        else:
            return "FAIL"
        

    def handle_authentication(self, action, name=None, surname=None, tel_number=None, email=None, username=None, password=None):
        if action == "register":
            result = self.create_account(name, surname, tel_number, email, username, password)
        else:  # action == "login"
            result = self.login(username, password)

        member_instance = self.find_member_by_username(username)

        if (result in ["LOGIN SUCCESS"]):
            session.login(member_instance)
            if (isinstance (member_instance,Member)):
                member_instance.add_basket(Basket())
                return Redirect("/")
        
            elif(isinstance (member_instance,Manager)):
                return Redirect("/manager")
        
        elif result in ["CREATE ACCOUNT SUCCESS"]:
            return Redirect("/")
        else:
            return f"{action.capitalize()} Failed. Try again"

    def add_all_menu_to_branch(self,menu,amount):
        for branch in self.__branches:
            stock = Stock(menu,amount)
            branch.add_stock(stock)
        return "Success"

    def add_food_list(self,food):
        self.__menu_list.append(food)
        return "Success"
    
    def add_food(self, type , name , id , price : int , picture  , amount = 1 ,  select = False ):
        menu = None
        if type == "Savory":
            menu =Savory(name,id,price, picture, select)
        elif type == "Dessert":
            menu = Dessert(name,id,price,picture , select)
        else:
            menu = Drink(name,id,price,picture , select)

        self.add_all_menu_to_branch(menu,amount)
        self.add_food_list(menu)
        return "Success"
        

    def find_menu_by_menu_id(self, menu_list: List[str]):
        menu_instance = []
        for menu in menu_list:
            for food in self.__menu_list:
                if menu == food.get_food_id():
                    menu_instance.append(food)

        return menu_instance

    def add_boxset_list(self, boxset_name: str, boxset_id: str, menu_list: List[str], price: int , picture):
        menu_instance = self.find_menu_by_menu_id(menu_list)
        self.__boxset_list.append(Boxset(boxset_name, boxset_id, menu_instance, price, picture))

    def search_boxset_by_id(self, boxset_id: str):
        for boxset in self.__boxset_list:
            if boxset.get_boxset_id() == boxset_id:
                return boxset
    
    def search_food_by_id(self, food_id : str):
        for food in self.__menu_list:
            if food.get_food_id() == food_id:
                return food
            
    def add_boxselect(self, food_type: str, menu_list: List[str], boxset_id: str ):
        menu_instance = self.find_menu_by_menu_id(menu_list)
        boxselect = BoxSelect(food_type, menu_instance )
        boxset_instance = self.search_boxset_by_id(boxset_id)
        if boxset_instance:
            boxset_instance.add_box_select(boxselect)

    def get_boxset_list(self):
        return self.__boxset_list

    def choose_boxset(self, boxset_id: str, select_list: list , quantity : int):
        boxset_instance = self.search_boxset_by_id(boxset_id)
        
        new_boxset_instance = Boxset(boxset_instance.get_name(),boxset_instance.get_boxset_id(),boxset_instance.get_fixed_menu(),boxset_instance.get_price(),boxset_instance.get_picture())
        new_boxset_instance.add_selected_menu(select_list)
        
        session.get_current_user().get_current_basket().add_basket_item(new_boxset_instance,quantity)
    
    def choose_menu(self,food_id :str , quantity : int , level : str):
        food_instance = self.search_food_by_id(food_id)
        duplicate_food = copy.deepcopy(food_instance)
        if level != None:
            duplicate_food.set_level(level)
        session.get_current_user().get_current_basket().add_basket_item(duplicate_food,quantity)

    def serch_food_instance_by_id(self,food_id):
        for menu in self.__menu_list:
            if menu.get_food_id() == food_id:
                return menu
            
    def add_promotion(self, promotion):
        self.__promotion_list.append(promotion)
    
    def remove_promotion(self, promotion):
        if promotion in self.__promotion_list:
            self.__promotion_list.remove(promotion)
    
    def get_coupon(self, coupon_code):
        for promotion in self.__promotion_list:
            if promotion.verify_coupon(coupon_code):
                print(f"Coupon {coupon_code} found with {promotion.get_discount()*100}% discount")  # Debugging
                return promotion
        print(f"Coupon {coupon_code} not found")  # Debugging
        return None

    def add_pickup_branch(self,branch_info):
        for branch in self.__branches:
            branch_address = branch.get_address()
            branch_district = branch.get_district()

            if branch_address == branch_info['address'] and branch_district == branch_info['district']:
                return branch
        return None
    

    def add_branch(self,zip,district,province):

        branch = Branch(zip,district,province)
        self.__branches.append(branch)

    def find_branch_from_post(self, post_number: str):
        try:
            post_number = int(post_number)
        except ValueError:
            return [] 

        matched_branches = [branch.get_branch_info() for branch in self.__branches if str(branch.get_branch_info()['postcode']) == str(post_number)]
        return matched_branches

    def search_branches(self, postcode: str):
        branch_list = self.find_branch_from_post(postcode)
        if branch_list:
            return Div(
                *[
                    Div(
                        Div(
                            H3(f"สาขา : {branch['district']}", cls="branch-title"),
                            P(f"ที่อยู่ : {branch['address']}", cls="branch-address"),
                            Button("เลือก",
                                   hx_post="/select_branch",
                                   hx_vals={  # เพิ่ม postcode
                                        "district": branch["district"], 
                                        "address": branch["address"],
                                        "postcode" : postcode
                                        },
                                   hx_target="#selected_branch",
                                   cls="select-button"
                            )
                        ),
                        cls="branch-card"
                    )
                    for branch in branch_list
                ]
            )
        else:
            return B("ไม่พบสาขาสำหรับรหัสไปรษณีย์นี้", cls="no-branch")
    
    def add_rider(self,name,surname,tel_number,email,postcode):
        rider = Rider(name,surname,tel_number,email,postcode)
        for branch in self.__branches:
            if branch.get_postcode() == postcode:
                branch.add_rider(rider)
                return "ADD RIDER SUCCESS"

    def get_stock_by_food_name(self, name):
        for stock in self.__stock:
            if(stock.get_product.get_name == name):
                return stock

    def get_delete_menu(self):
        return self.__delete_list
    
    def create_member(self, name, surname, account_ID, tel_no, address, email, username, password):
        new_member = Member(name, surname, account_ID, tel_no, address, email, username, password, Basket())
        self.__member_list.append(new_member)
        return new_member

    def get_coupon(self, coupon_code):
        for promotion in self.__promotion_list:
            if promotion.verify_coupon(coupon_code):
                return promotion
        return None

    def summary_order(self):

        member = session.get_current_user()
        if not member:
            return None
        return member.summary_order()  # ส่ง system เข้าไปด้วย
    
    def find_near_branch(self, address):
        for branch in self.__branches:
            postcode = str(branch.get_postcode())  # แปลง postcode เป็น string
            if postcode in address:
                return branch
            
        return None
    
    def find_branch_by_post_code(self,postcode):
        for branch in self.__branches:
            if branch.get_postcode() == postcode:
                return branch

class OrderHistory:
    __current_order_id = 67010000

    def __init__(self, member_id , order_type , basket, rider = None ):
        self.__member = member_id
        self.__order_ID = OrderHistory.__current_order_id
        OrderHistory.__current_order_id += 1  
        self.__order_type = order_type 
        self.__basket = basket
        self.__rider = rider
        
    def get_order_id(self):
        return self.__order_ID

    def get_order_type(self):
        return self.__order_type
    
class Account:
    __current_member_id = 1000000
    def __init__(self,name,surname,tel_number,email):
        self.__name = name
        self.__surname = surname
        self.__tel_number = tel_number
        self.__email = email
        self.__account_id = Account.__current_member_id
        Account.__current_member_id += 1

    def get_account_name(self):
        return self.__name
    
    def get_account_surname(self):
        return self.__surname
    
    def get_email(self):
        return self.__email
    
    def get_account_id(self):
        return self.__account_id

    def get_member_info(self):
        return [self.__name, self.__surname, self.__account_id, self.__tel_number, self.__email] 

    @property
    def get_id(self):
        return self.__account_id
    
class Delivery:
    def __init__(self):
        self.__address = None
        self.__branch = None

    def get_address(self):
        return self.__address
    
    def set_address(self, address_info: str):
        self.__address = address_info
        branch = system.find_near_branch(address_info)
        self.set_branch(branch)   
        
        return "Done"

    def set_branch(self,branch : 'Branch'): #instance branch
        self.__branch = branch

    def get_branch(self):
        return self.__branch
    
class PickUp:
    def __init__(self):
        self.__selected_branch = None
        self.__branch = None

    def get_selected_branch(self):
        return self.__selected_branch

    def set_branch(self, branch_info):
        self.__selected_branch = branch_info
        self.select_branch()
        return "Done"

    def select_branch(self):
        branch = system.add_pickup_branch(self.__selected_branch)
        self.__branch = branch
        return "Done"

    def get_branch(self):
        return self.__branch



class Branch:
    def __init__(self, postcode, district, address):
        self.__postcode = postcode
        self.__district = district
        self.__address = address
        self.__rider_list = []
        self.__stock_list = []
    def get_branch_info(self):
        return {
            "postcode": self.__postcode,  
            "district": self.__district,  
            "address": self.__address
        }
    
    def get_address(self):
        return self.__address
    
    def get_district(self):
        return self.__district
    def add_rider(self,rider):
        self.__rider_list.append(rider)        
    
    def get_postcode(self):
        return self.__postcode
    
    def get_rider(self):
        return self.__rider_list
    
    def get_branch_address(self):
        return f"สาขา: {self.__postcode} เขต: {self.__district} จังหวัด: {self.__address}"
    
    def add_stock(self,stock):
        self.__stock_list.append(stock)
        return "Success"

    def reduce_stock(self,food,quantity : int):
        
        stock = self.find_stock_by_food(food)

        result = stock.reduce_quantity(quantity)
        if result:
            return "Success"
        
        return None
    
    def find_stock_by_food(self,food):
        for stock in self.__stock_list:
            if stock.get_food().get_food_id() == food.get_food_id():
                return stock
            
        return None
class Manager(Account):
    def __init__(self, name, surname, tel_number, email,username,password):
        super().__init__(name, surname, tel_number, email)
        self.manage_history = []
        self.__username = username
        self.__password = password

    def add_manage_history(self,type,menu_id):
        self.manage_history.append(f"{type} : {menu_id}")

    def get_username(self):
        return self.__username

    def verify(self, password):
        if self.__password == password:
            return "LOGIN SUCCESS"
        else:
            return "LOGIN FAIL"
        
    def get_username(self):
        return self.__username


class Member(Account):
    def __init__(self, name, surname, tel_number, email,username,password):
        super().__init__(name, surname, tel_number, email)
        self.__username = username
        self.__password = password
        self.__current_basket = None
        self.__order_type = None
        self.__order_history = []

    def add_order_history(self,order,Order):
        self.__order_history.append(order)

    def get_order_type(self):
        return self.__order_type
    
    def add_order_type(self,order):
        self.__order_type = order

    def get_username(self):
        return self.__username
    
    def add_delivery(self,delivery):
        self.__delivery = delivery

    def make_new_order(self):
        self.__current_basket = Basket()

    def change_password(self, old_password, new_password):
        if old_password == self.__password:
            self.__password = new_password
            return "Password changed successfully!"
        else:
            return "Old password is incorrect."

    def verify(self, password):
        if self.__password == password:
            return "LOGIN SUCCESS"
        else:
            return "LOGIN FAIL"

    def add_basket(self,basket):
        self.__current_basket = basket
    
    def get_current_basket(self):
        return self.__current_basket
    
    def view_basket(self, coupon_code=None):
        return self.__current_basket.item_selected(coupon_code)
    
    def summary_order(self):
        user_info = self.get_member_info()
        
        items, total_price, discount_applied, discount_include = self.__current_basket.item_selected()
        order_type = self.__order_type
        return [user_info, items, discount_include, order_type, discount_applied]
    
    def create_order_history(self,rider = None):
        order_history = OrderHistory(self.get_account_id(), self.__order_type, self.__current_basket,rider)
        self.add_order_history(order_history)
        return order_history
    
    def add_order_history(self,order):
        self.__order_history.append(order)
        return "Done"
    
    def reset_basket(self):
        self.__current_basket = Basket()
    
    def get_order_history(self):
        return self.__order_history
class PickedItem:
    def __init__(self, product, quantity: int):
        self.item_id = uuid4().hex
        self.__product = product  
        self.__quantity = quantity

    def get_item_info(self):
        
        return {
            
            "name": self.__product,
            "item_id": self.item_id,
            "quantity": self.__quantity
        }   

    def get_product(self):
        return self.__product

    def get_total(self):
        return self.__quantity
    
    def increase_quantity(self, total: int):
        self.__quantity += int(total)


class Basket:
    def __init__(self):
        self.__items = []
        self.__coupon_code = ""
    
    def get_item_in_basket(self):
        return self.__items
    

    def check_empty(self):
        return bool(self.__items)  # คืนค่า True ถ้ามีสินค้าอยู่ในตะกร้า
    
    def check_exist(self, item):

        if isinstance(item,Boxset):
            for pickedbasket in self.__items:
                boxset = pickedbasket.get_product()
                if isinstance(boxset, Boxset):
                    if (item.get_boxset_id() == boxset.get_boxset_id()) and (item.get_selected_menu() == boxset.get_selected_menu()):
                        return pickedbasket  # ✅ คืน PickedItem เดิม ถ้าพบ
        elif isinstance(item,Food):
            for pickedbasket in self.__items:
                food = pickedbasket.get_product()
                if isinstance(food,Food):
                    if (item.get_food_id() == food.get_food_id()) and (item.get_select() == food.get_select()):
                        return pickedbasket

        return None

    
    def add_basket_item(self, item, quantity: int):
        pickeditem = PickedItem(item, int(quantity))

        if (isinstance(item,Boxset)) or (isinstance(item,Food)):
            check_exist = self.check_exist(item)

            if isinstance (check_exist,PickedItem):
                check_exist.increase_quantity(int(quantity))  # เพิ่มจำนวนถ้ามีอยู่แล้ว
                return "Done"

            self.__items.append(pickeditem)
            return "Done"

        
    def remove_basket_item(self, item_name):
        self.__items = [item for item in self.__items if item.get_item_info()["name"] != item_name]

    def change_quantity(self, item_id: str, change: int):
        if change not in (-1, 1):
            return False
        for item in self.__items:
            if item.item_id == item_id:
                item.increase_quantity(change)
                if item.get_total() <= 0:
                    self.__items.remove(item)
                return True
        return False

    def get_coupon_code(self):
        return self.__coupon_code

    def calculate_payable_total(self):
        return self.item_selected()[3]

    def calculate_total_price(self):
        total_price = 0
        for pickeditem in self.__items:
            product = pickeditem.get_product()
            total_price += int(int(product.get_price()) *int( pickeditem.get_total()))

        return total_price

    def item_selected(self, coupon_code=None):
        if coupon_code is not None:
            self.__coupon_code = coupon_code
        coupon_code = self.__coupon_code
        items = [item.get_item_info() for item in self.__items]
        total_price = self.calculate_total_price()
        discount_applied = 0
        discount_include = total_price  # ตั้งค่าให้เริ่มต้นเป็นราคาปกติ

        if coupon_code:
            promotion = system.get_coupon(coupon_code)
            if promotion:
                discount_applied = total_price * promotion.get_discount()
                discount_include = total_price - discount_applied  # ราคาหลังลด

        return items, total_price, discount_applied, discount_include

class Food:
    def __init__(self, food_name: str, food_id: str, price: int , picture ):
        self.__food_name = food_name
        self.__food_id = food_id
        self.__food_price = price
        self.__food_picture = picture
        self.__status = "AVAILABLE"

    def change_status(self):
        self.__status = None

    def check_status(self):
        return self.__status
    
    def get_name(self):
        return self.__food_name

    def get_food_id(self):
        return self.__food_id

    def get_price(self):
        return self.__food_price

    def get_id(self):
        return self.__food_id
    
    def get_picture(self):
        return self.__food_picture
    
class Savory(Food):
    def __init__(self, food_name, food_id, price , picture, spicy_level = None ):
        super().__init__(food_name, food_id, price, picture)
        self.__spicy_level = spicy_level

    def get_select(self):
        return self.__spicy_level

    def set_level(self,level):
        self.__spicy_level = level

class Dessert(Food):
    def __init__(self, food_name, food_id, price , picture, type = None):
        super().__init__(food_name, food_id, price,picture)
        self.__sugar_free = type

    def get_select(self):
        return self.__sugar_free
    
class Drink(Food):
    def __init__(self, food_name, food_id, price , picture , sweet_level = None):
        super().__init__(food_name, food_id, price , picture)
        self.__sweet_level = sweet_level
    
    def get_select(self):
        return self.__sweet_level

    def set_level(self,level):
        self.__sweet_level = level

class Stock:
    def __init__(self, food_instance: Food, amount: int):
        self.__food = food_instance
        self.__amount = amount

    def reduce_amount(self, total: int):
        self.__amount -= total

    def get_food(self):
        return self.__food

    def add_stock(self,total : int):
        self.__amount += total

    def get_total_amount(self):
        return self.__amount
    
    def reduce_quantity(self, quantity : int):
        total = self.__amount - int(quantity)
        if total >= 0:
            self.__amount = total
            return "Done"
        
        return None
class Boxset:
    def __init__(self, name: str, boxset_id: str, menu: List[Food], price: int, picture):
        self.__boxset_name = name
        self.__boxset_id = boxset_id
        self.__fixed_menu = menu
        self.__price = price
        self.__boxselect = []
        self.__selected_menu = []
        self.__picture = picture

    def get_boxset_id(self):
        return self.__boxset_id

    def add_box_select(self, box_select):
        self.__boxselect.append(box_select)

    def get_name(self):
        return self.__boxset_name

    def get_fixed_menu(self):
        return self.__fixed_menu

    def get_box_select_list(self):
        return self.__boxselect

    def get_price(self):
        return self.__price
    
    def add_selected_menu(self,selected_menu : list):
        for menu in selected_menu:
            self.__selected_menu.append(menu)

    def get_selected_menu(self):
        return self.__selected_menu
    

    def get_picture(self):
        return self.__picture
    
class BoxSelect:
    def __init__(self, menu_type: str, select_option: List[Food] ):
        self.__menu_type = menu_type
        self.__select_option = select_option
        
        

    def select_good_in_set(self, selected: Food):
        if selected in self.__select_option:
            self.__selected_menu = selected

    def get_menu_type(self):
        return self.__menu_type

    def get_select_option(self):
        return self.__select_option

    
    
    def get_select_option_id(self):
        return [id.get_food_id() for id in self.__select_option]

    
class Promotion:
    def __init__(self, coupon_code, discount):
        self.__coupon_code = coupon_code
        self.__discount = discount
    
    def verify_coupon(self, coupon_code):
        return self.__coupon_code == coupon_code
    
    def get_discount(self):
        return self.__discount

class SessionManager:
    def __init__(self):
        self.current_user = None 
    
    def login(self, username):
        self.current_user = username  

    def logout(self):
        self.current_user = None 

    def get_current_user(self):
        return self.current_user

class Rider(Account):
    def __init__(self, name, surname, tel_number, email,branch):
        super().__init__(name, surname, tel_number, email)
        self.__branch = branch
        self.__work_status = "FREE"
        self.__delivery_history = []
    
    def add_delivery_history(self,delivert_history):
        self.__delivery_history.append(delivert_history)

    def check_free(self):
        if self.__work_status == "FREE":
            return "FREE"
        return "BUSY"
    
    def set_free(self):
        self.__work_status = "FREE"
    
    def set_busy(self):
        self.__work_status = "BUSY"

    def get_branch(self):
        return self.__branch
    
    def get_branch_info(self):
        return self.__branch.get_branch_address()
session = SessionManager()        
system = System()
member = system.create_account("sky","sinthaveelert","0613153416","badinskysky@gmail.com","skyzaza","1234")
manager = system.add_admin("Sky","Sinthaveelert","0613153416","badinskysky@gmail.com","sky","1234")
system.add_branch("10200", "พระนคร", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10300", "ดุสิต", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10530", "หนองจอก", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10500", "บางรัก", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10220", "บางเขน", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10240", "บางกะปิ", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10330", "ปทุมวัน", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10100", "ป้อมปราบศัตรูพ่าย", "กรุงเทพ,ประเทศไทย"),
system.add_branch("10260", "พระโขนง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10510, "มีนบุรี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10520, "ลาดกระบัง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "ยานนาวา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10100, "สัมพันธวงศ์", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "พญาไท", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "ธนบุรี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "บางกอกใหญ่", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10310, "ห้วยขวาง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10600, "คลองสาน", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10170, "ตลิ่งชัน", "กรุงเทพ, ประเทศไทย"),
system.add_branch(10700, "บางกอกน้อย", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "บางขุนเทียน", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10160, "ภาษีเจริญ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10140, "ราษฎร์บูรณะ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10700, "บางพลัด", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "ดินแดง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "บึงกุ่ม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "สาทร", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10800, "บางซื่อ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10900, "จตุจักร", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10120, "บางคอแหลม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10250, "ประเวศ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10110, "คลองเตย", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10250, "สวนหลวง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "จอมทอง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10210, "ดอนเมือง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10400, "ราชเทวี", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10230, "ลาดพร้าว", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10110, "วัฒนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "สะพานสูง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10100, "สัมพันธวงศ์", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10220, "สายไหม", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10230, "คันนายาว", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10240, "สะพานสูง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10310, "วังทองหลาง", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10510, "คลองสามวา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10260, "บางนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10170, "ทวีวัฒนา", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10140, "ทุ่งครุ", "กรุงเทพ,ประเทศไทย"),
system.add_branch(10150, "บางบอน", "กรุงเทพ,ประเทศไทย")

branches = [
    (10200, "พระนคร"), (10300, "ดุสิต"), (10530, "หนองจอก"), (10500, "บางรัก"),
    (10220, "บางเขน"), (10240, "บางกะปิ"), (10330, "ปทุมวัน"), (10100, "ป้อมปราบศัตรูพ่าย"),
    (10260, "พระโขนง"), (10510, "มีนบุรี"), (10520, "ลาดกระบัง"), (10120, "ยานนาวา"),
    (10100, "สัมพันธวงศ์"), (10400, "พญาไท"), (10600, "ธนบุรี"), (10600, "บางกอกใหญ่"),
    (10310, "ห้วยขวาง"), (10600, "คลองสาน"), (10170, "ตลิ่งชัน"), (10700, "บางกอกน้อย"),
    (10150, "บางขุนเทียน"), (10160, "ภาษีเจริญ"), (10140, "ราษฎร์บูรณะ"), (10700, "บางพลัด"),
    (10400, "ดินแดง"), (10240, "บึงกุ่ม"), (10120, "สาทร"), (10800, "บางซื่อ"),
    (10900, "จตุจักร"), (10120, "บางคอแหลม"), (10250, "ประเวศ"), (10110, "คลองเตย"),
    (10250, "สวนหลวง"), (10150, "จอมทอง"), (10210, "ดอนเมือง"), (10400, "ราชเทวี"),
    (10230, "ลาดพร้าว"), (10110, "วัฒนา"), (10240, "สะพานสูง"), (10100, "สัมพันธวงศ์"),
    (10220, "สายไหม"), (10230, "คันนายาว"), (10240, "สะพานสูง"),
    (10310, "วังทองหลาง"), (10510, "คลองสามวา"), (10260, "บางนา"), (10170, "ทวีวัฒนา"),
    (10140, "ทุ่งครุ"), (10150, "บางบอน")
]

# Create two riders for each branch with post code only
for branch_code, branch_name in branches:
    # Create two riders for each branch
    rider1 = system.add_rider("Rider1","ABC", "1234567890", "rider1@ABC.com",branch_code)
    rider2 = system.add_rider("Rider2", "EFG", "0987654321","rider2@EFG.com",branch_code)



system.add_food("Savory", "ไก่ทอดสูตรผู้พันโดม","10001",39 , "https://images.ctfassets.net/n4pc9wlortyn/1PTqNXLJLaeEmb1OB3Crgr/772c24e56b996d1c8894d355a6dca910/1_pc._Fried_Chicken_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "ไก่วิงซ์แซ่บ 2 ชิ้น","10002",75 , "https://images.ctfassets.net/n4pc9wlortyn/5NMycxbXDszGSlDBQ0LEEW/18470f88d6aeca847329d2ccc2de7940/2_pcs._WingZ_Zabb_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "ไก่ไม่มีกระดูก 2 ชิ้น", "10003" , 75 , "https://images.ctfassets.net/n4pc9wlortyn/1lUP8d7TNIwllDocIHuy7o/d4b6b241aec6fc8f9074bf982d0853a5/2_pcs._Crispy_Strip_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory", "นักเก็ตส์  7 ชิ้น" , "10004" , 50 , "https://images.ctfassets.net/n4pc9wlortyn/ixqPr5roRfvh88mGjAQi8/3b2fb1630828999a6045d7309ac0df9a/7_pcs._Chicken_Pop_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "กุ้งโดนัท 1 ชิ้น" , "10005" , 55 , "https://images.ctfassets.net/n4pc9wlortyn/6QPqFn9J7F68ubgbb16u1j/e4463b4b52808563fbd688224857645d/Shrimp_Donut_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "ทาร์ตไข่ 1 ชิ้น" , "10006", 35 , "https://images.ctfassets.net/n4pc9wlortyn/6eueZZxvmoj0TyEDoiHT2K/342d84453f0f7bab4481cb82cde0e1d3/1_pc._Egg_Tart_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100)
system.add_food("Savory" , "ข้าวไก่กรอบ" , "10007" , 60 ,"https://images.ctfassets.net/n4pc9wlortyn/5CHcoRrT9cSHrtQfYQXZst/e3c61128536a29d7c5a80cded0aee179/Spicy_Chicken_Rice_Bowl_480x388.png?h=600&w=800&fm=webp&fit=fill",amount = 100,select=True)
system.add_food("Savory" , "ข้าวแกงเขียวหวานไก่" , "10008", 89 , "https://images.ctfassets.net/n4pc9wlortyn/5ibn1iVcubtz7LLDwedId9/c04976ee0489aea0c76468fb7b55497a/Green_Curry_Rice_Bowl_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100,select=True)
system.add_food("Savory" , "ข้าวหอมมะลิ" , "10009" , 35 , "https://images.ctfassets.net/n4pc9wlortyn/OXZHelDGLBtXt6nux2TkH/8a1c60461d1010ac1489ca608b48dad1/Plain_Rice_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100)

system.add_food("Dessert" , "Solf Serve" , "11000", 19 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558434037.png", amount = 100)
system.add_food("Dessert" , "Donut Spinkle" , "11001" , 35 , "http://www.misterdonut.co.th/upload_file/menu/170420101412_02-Suger-Raise-big.png", amount = 100)
system.add_food("Dessert" , "Chocolate Sunday" , "11002" , 35 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558601385.png", amount = 100)
system.add_food("Dessert" , "Strawberry Sunday" , "11003" , 35 , "https://s3-ap-southeast-1.amazonaws.com/cdn.dairyqueenthailand.com/images/1558601312.png" , amount = 100) 

system.add_food("Drink" , "Pepsi" , "12000" , 20 , "https://images.ctfassets.net/n4pc9wlortyn/6vvUyuXaRROoCVhOY3nmLX/a248ffc9305534fbdedb16e695ee3892/Pepsi_1_Glass_480x388.png?h=600&w=800&fm=webp&fit=fill" , amount = 100)
system.add_food("Drink" , "Mineral Water" , "12001" , 15 , "https://images.ctfassets.net/n4pc9wlortyn/4l7HHuczM6P3Y2gL6F5282/3b7876ba9331342253b1d4a2ebe22491/Mineral_Water_480x388.png?h=600&w=800&fm=webp&fit=fill" ,amount = 100)
system.add_food("Drink" , "Drink-7" , "12002" , 20 , "https://images.ctfassets.net/n4pc9wlortyn/gyIOI9C9CoZNqdzKh2CYQ/ff975f64f6334b2882837c4c746aea02/7-Up_No_Sugar_480x388.png?h=600&w=800&fm=webp&fit=fill")
system.add_food("Drink" , "Matcha" , "12003", 35 ,"https://images.ctfassets.net/n4pc9wlortyn/2faQl2VCe9TYtYL0JINtWR/e9fe656929dd3b1c806b713c1c55e8bd/Iced_Matcha_Latte_16oz_480x388.png?h=600&w=800&fm=webp&fit=fill" , amount = 100  ,select=True)
system.add_food("Drink" , "Espresso" , "12004" , 35,"https://images.ctfassets.net/n4pc9wlortyn/SmlGNIBr0mCxoeCtrm9vS/9bf614db87a44eeb7036ad0ae667c269/IcedEspresso_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True )
system.add_food("Drink" , "Chocolate" , "12005" , 40 ,"https://images.ctfassets.net/n4pc9wlortyn/5gEPCPZ82XxSb36U7brrfP/52ea873bd8e41d5c9a19336a0efdff85/IcedChocolate_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True )
system.add_food("Drink" , "Pink Milk" , "12006", 40 ,"https://images.ctfassets.net/n4pc9wlortyn/7BEkkFswnPpISyARO0zOc2/da0218514b5079ee9368d4cdd1aea38c/IcedPinkyMilk_480x388.png?h=600&w=800&fm=webp&fit=fill", amount = 100 , select=True)

system.add_boxset_list("ชุดอิ่มแน่นอน", "1001", ["10001", "10006"], 500, "https://images.ctfassets.net/n4pc9wlortyn/7MQe9UhiKuB8gLMXorUorW/f0173ffc64c4b12ea3c11831634359df/Party-Buldak-wingz.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดสุดคุ้ม", "1002", ["10008", "12002"], 100,"https://images.ctfassets.net/n4pc9wlortyn/7BoZpkNiyICqN9CLgBl9J8/3806c7658e37067c0e395eae8b31cf3b/JPU_The_Box_Signature_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดไก่เลิฟเวอร์", "1003", ["10002", "10001"], 50, "https://images.ctfassets.net/n4pc9wlortyn/1VynJvkHfHS2QFjNLvvjYS/a61598f75cae5c805d255180d4b12746/JPU_The_Box_All_Rice_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดเครื่องเคียง", "1004", ["10005", "10006"], 180, "https://images.ctfassets.net/n4pc9wlortyn/561btRzoDxiDE4atf9Miih/2a4833d320c9938f5323a7d74c203ac7/JPU_Im_Suk_Jai_480x388.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดอิ่มไหม", "1005", ["10007", "10005"], 50, "https://images.ctfassets.net/n4pc9wlortyn/3J3gMlQgk3yI9LxUD2YqGn/2ea86690e0a84f03e7f3afb2899664c4/The-box-Buldak-wingz.png?h=900&w=1200&fm=webp&fit=fill")
system.add_boxset_list("ชุดไก่กรอบอร่อย", "1006", ["10002", "11003"], 100, "https://images.ctfassets.net/n4pc9wlortyn/6xIGgEQ7eJdaKdTRSUGajq/6d5552112fa3f6fbdbbc86890f355309/JPU_Zinger_Set_480x388.png?h=900&w=1200&fm=webp&fit=fill")

system.add_boxselect("เครื่องดื่มโดนใจ", ["12000", "12001","12002"], "1001")
system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1001")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1002")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006"], "1002")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1003")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003","11001"], "1004")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006","10004"], "1004")
system.add_boxselect("ข้าวเซ็ตโดนใจ", ["10009", "10008"], "1004")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003","11001"], "1005")
system.add_boxselect("เครื่องเคียงโดนใจ", ["10005", "10006","10004"], "1005")

system.add_boxselect("ของหวานถูกใจ", ["11002", "11003"], "1006")

system.add_promotion(Promotion("DISCOUNT10", 0.10))  # ส่วนลด 10%
system.add_promotion(Promotion("DISCOUNT20", 0.20))  # ส่วนลด 20%


def navbar():
    if session.get_current_user():  # Check if the current user is logged in
        user = Div(
            Button("CART", onclick="window.location.href='/basket';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            Button("LOGOUT", onclick="window.location.href='/logout';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
            "margin-left": "auto"
            }
        )
    else:
        user = Div(
            Button("CART", onclick="window.location.href='/basket';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
            Button("LOGIN", onclick="window.location.href='/login';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
            Button("Sign In", onclick="window.location.href='/register';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
                "margin-left": "auto"
        }
        )


    return Div(
        Button("OUR SERVICE", onclick="window.location.href='/';",style={
            "font-weight" : "700",
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "36px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("Menu",onclick="window.location.href='/menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        user,
        cls="site-navbar",
        style={
            "background-color" : "white",
            "display": "flex",
            "align-items": "center",
            "width": "100%"
        }
    )

def managebar():
    user = Div(
            
            Button("LOGOUT", onclick="window.location.href='/logout';", style={
            "font-weight": "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
            }),
            style={
            "background-color": "white",
            "display": "flex",
            "gap": "20px",
            "margin-left": "auto"
            }
        )
    
    return Div(
        Button("OUR SERVICE", onclick="window.location.href='/manager';",style={
            "font-weight" : "700",
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "36px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("MenageMenu",onclick="window.location.href='/manage_menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("RestoreMenu",onclick="window.location.href='/restore_delete_menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        Button("MenuDetail",onclick="window.location.href='/menu';", style={
            "font-weight" : "500",
            "background": "none",
            "border": "none",
            "color": "black",
            "font-size": "16px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        user,
        style={
            "background-color" : "white",
            "display": "flex",
            "align-items": "center",
            "width": "100%"
        }
    )

def order_section():
    member = session.get_current_user()
    if isinstance(member,Manager):
        return Div(
            H5("WELCOME MANAGER", style={
                "color": "white",
                "margin-top": "20px",
                "text-align": "center",  # จัดกลางข้อความ
            }),
            style={
                "background-color": "black",
                "color": "white",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "height": "10vh",
                "width": "100%",  # เปลี่ยนจาก 100vw เป็น 100% ป้องกันล้น
                "max-width": "100vw",  # จำกัดไม่ให้เกินจอ
                "margin": "0 auto",  # จัดให้อยู่ตรงกลาง
                "padding": "0",
                "box-sizing": "border-box",
                "overflow-x": "hidden",
            }
        )
    order_type = member.get_order_type() if member else None

    # กรณีที่ยังไม่ได้เลือกประเภทการสั่งซื้อ
    if not order_type:
        return Div(
            H5("LET'S ORDER FOR PICK UP OR DELIVERY", style={
                "color": "white",
                "margin-top": "20px",
                "text-align": "center",  # จัดกลางข้อความ
            }),
            Button("Start Order", onclick="window.location.href='/selectdelivery';", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
            style={
                "background-color": "black",
                "color": "white",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "height": "10vh",
                "width": "100%",  # เปลี่ยนจาก 100vw เป็น 100% ป้องกันล้น
                "max-width": "100vw",  # จำกัดไม่ให้เกินจอ
                "margin": "0 auto",  # จัดให้อยู่ตรงกลาง
                "padding": "0",
                "box-sizing": "border-box",
                "overflow-x": "hidden",
            }
        )
    
    # ถ้ามีการเลือกประเภทการสั่งซื้อแล้ว
    order_type_text = H2("Order Type : Delivery", style={"color": "white", "margin-top" : "15px"}) if isinstance(order_type, Delivery) else H2("Order Type : PICK UP", style={"color": "white", "margin-top" : "15px"})

    # สร้าง Div ที่แสดงประเภทการสั่งซื้อและปุ่ม Change
    return Div(
        order_type_text,
        Button("CHANGE", onclick="window.location.href='/selectdelivery';", style={
            "background": "none",
            "border": "none",
            "color": "red",
            "font-size": "24px",
            "cursor": "pointer",
            "padding": "10px 20px",
        }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    )
@rt("/logout")
def logout():
    session.logout()
    return Redirect("/")

def product_detail_page(item, category, options, action, fixed_menu=()):
    """Shared storefront detail layout for every food and box set."""
    price = item.get_price()
    return (
        Title(f"{item.get_name()} | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.product-page) { margin:0; background:#fff; }
            main.container:has(.product-page) { width:100%; max-width:none; padding:0; }
            .product-page { color-scheme:light; font-family:'K2D',sans-serif; color:#202020; background:#fff; min-height:100vh;
                --pico-color:#202020; --pico-h1-color:#202020; --pico-h2-color:#202020; --pico-h3-color:#202020; }
            .product-page *, .product-page *::before { box-sizing:border-box; }
            .product-page a { color:#c92027; text-decoration:none; }
            .product-page button, .product-page input, .product-page select { font-family:inherit; }
            .product-page :is(a,button,input,select):focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            .product-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .product-header button { width:auto; margin:0; }
            .product-order { background:#202020; }
            .product-order > div { width:100% !important; max-width:1280px !important; height:auto !important; min-height:66px; padding:12px 32px !important; gap:20px; flex-wrap:wrap; background:#202020 !important; }
            .product-order h2,.product-order h5 { margin:0 !important; font-size:15px; }
            .product-order button { width:auto; margin:0; background:#c92027 !important; color:white !important; font-size:14px !important; border-radius:3px; }
            .product-shell { max-width:1216px; margin:auto; padding:28px 32px 72px; }
            .product-breadcrumb { display:flex; flex-wrap:wrap; gap:10px; color:#777; font-size:14px; margin-bottom:28px; }
            .product-layout { display:grid; grid-template-columns:1.05fr 1fr; gap:56px; align-items:start; }
            .product-photo { position:relative; background:#f5f3ef; border-radius:8px; overflow:hidden; aspect-ratio:1.12; display:grid; place-items:center; }
            .product-photo img { width:100%; height:100%; object-fit:contain; }
            .product-tag { position:absolute; top:20px; left:20px; background:#fff; color:#c92027; font-size:12px; font-weight:700; padding:7px 12px; letter-spacing:.1em; }
            .product-eyebrow { font-size:12px; letter-spacing:.15em; color:#c92027; font-weight:700; margin:0 0 12px; }
            .product-page h1 { font-size:clamp(28px,3.5vw,42px); line-height:1.3; margin:0 0 12px; }
            .product-price { color:#c92027; font-size:30px; font-weight:700; margin:0 0 8px; }
            .product-muted { color:#707070; font-size:14px; margin:0; }
            .product-section { padding:24px 0; border-top:1px solid #e8e4df; margin-top:24px; }
            .product-page h2 { font-size:20px; margin:0 0 16px; }
            .product-fixed { display:flex; align-items:center; gap:14px; padding:10px 0; font-size:15px; }
            .product-fixed img { width:64px; height:56px; object-fit:contain; background:#f5f3ef; border-radius:4px; }
            .product-fixed span:last-child { margin-left:auto; color:#c92027; font-size:12px; white-space:nowrap; }
            .product-form { margin:0; }
            .product-option { margin-bottom:18px; }
            .product-option label { color:#202020; font-size:15px; font-weight:600; margin-bottom:8px; }
            .product-option select { background-color:#fff; color:#202020; border:1px solid #d9d5cf; border-radius:4px; margin:0; font-size:15px; }
            .product-purchase { padding-top:24px; border-top:1px solid #e8e4df; }
            .product-quantity-row,.product-total { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:20px; }
            .product-stepper { display:flex; align-items:center; border:1px solid #d9d5cf; border-radius:4px; overflow:hidden; }
            .product-stepper button { width:42px; height:44px; padding:0; margin:0; background:#fff; border:0; border-radius:0; color:#202020; font-size:22px; box-shadow:none; }
            .product-stepper button:disabled { opacity:.3; }
            .product-stepper input { width:58px; height:44px; text-align:center; border:0; margin:0; padding:0; color:#202020; background:#fff; appearance:textfield; box-shadow:none; }
            .product-stepper input::-webkit-inner-spin-button { appearance:none; }
            .product-total strong { font-size:24px; }
            .product-submit { width:100%; margin:0; padding:16px; background:#c92027; border:1px solid #c92027; color:#fff; border-radius:4px; font-weight:600; }
            .product-submit:hover { background:#a8171d; border-color:#a8171d; }
            .product-back { display:block; text-align:center; margin-top:16px; font-size:14px; }
            @media(max-width:760px) { .product-layout { grid-template-columns:1fr; gap:28px; } .product-shell { padding:20px 20px 40px; } .product-header > div { padding:12px 16px; } .product-header .site-navbar > button:first-child { font-size:25px !important; } .product-header .site-navbar > div { gap:0 !important; flex-wrap:wrap; } .product-order > div { padding:12px 20px !important; gap:8px; } .product-photo { aspect-ratio:1.3; } }
        """),
        Div(
            Div(navbar(), cls="product-header"),
            Div(order_section(), cls="product-order"),
            Div(
                Div(A("หน้าหลัก", href="/"), Span("/"), A("เมนูอาหาร", href="/menu"), Span("/"), Span(item.get_name()), cls="product-breadcrumb", aria_label="เส้นทางหน้า"),
                Div(
                    Div(
                        Div(Span(category, cls="product-tag"),
                            Span("ยังไม่มีรูปภาพ", hidden=True),
                            Img(src=item.get_picture(), alt=item.get_name(), width="600", height="520", onerror="this.hidden=true; this.previousElementSibling.hidden=false;"), cls="product-photo"),
                        Section(H2("ในชุดนี้มี"), *[
                            Div(Img(src=food.get_picture(), alt="", loading="lazy", onerror="this.hidden=true"), Strong(food.get_name()), Span("รวมในชุด"), cls="product-fixed")
                            for food in fixed_menu
                        ], cls="product-section") if fixed_menu else None,
                    ),
                    Div(
                        P(category, cls="product-eyebrow"), H1(item.get_name()),
                        P(f"฿{price:,.0f}", cls="product-price"), P("ราคาต่อชุด" if fixed_menu else "ราคาต่อรายการ", cls="product-muted"),
                        Form(
                            Section(H2("เลือกความอร่อยของคุณ"), *options, cls="product-section") if options else Section(P("พร้อมเสิร์ฟความอร่อย เลือกจำนวนที่ต้องการได้เลย", cls="product-muted"), cls="product-section"),
                            Div(
                                Div(Label("จำนวน", fr="product-quantity"),
                                    Div(Button("−", type="button", data_step="-1", aria_label="ลดจำนวน", disabled=True),
                                        Input(type="number", id="product-quantity", name="counter_value", value="1", min="1", max="99", step="1", required=True, aria_label="จำนวนสินค้า"),
                                        Button("+", type="button", data_step="1", aria_label="เพิ่มจำนวน"), cls="product-stepper"), cls="product-quantity-row"),
                                Div(Span("ราคารวม"), Strong(f"฿{price:,.0f}", id="product-total", aria_live="polite"), cls="product-total"),
                                Button("เพิ่มลงตะกร้า", type="submit", cls="product-submit"),
                                A("← กลับไปเลือกเมนู", href="/menu", cls="product-back"), cls="product-purchase"),
                            action=action, method="post", cls="product-form", data_price=str(price),
                        ),
                    ), cls="product-layout"), cls="product-shell"), cls="product-page"),
        Script("""
            (() => {
                const form = document.querySelector('.product-form');
                const quantity = form.querySelector('[name=counter_value]');
                const buttons = form.querySelectorAll('[data-step]');
                function update() {
                    const value = Math.max(1, Math.min(99, Math.floor(Number(quantity.value) || 1)));
                    quantity.value = value;
                    document.getElementById('product-total').textContent = '฿' + (value * Number(form.dataset.price)).toLocaleString('th-TH');
                    buttons[0].disabled = value <= 1;
                    buttons[1].disabled = value >= 99;
                }
                buttons.forEach(button => button.addEventListener('click', () => {
                    quantity.value = Number(quantity.value) + Number(button.dataset.step); update();
                }));
                quantity.addEventListener('input', update);
                form.addEventListener('submit', update);
            })();
        """),
    )


def product_option(label, name, values, index):
    field_id = f"product-option-{index}"
    return Div(Label(label, fr=field_id), Select(*[Option(value, value=value) for value in values],
               name=name, id=field_id, required=True), cls="product-option")


@rt("/boxset/{boxset_id}")
def boxset_detail(boxset_id: str):
    boxset = system.search_boxset_by_id(boxset_id)
    if not boxset:
        return P("Boxset not found.")
    options = [product_option(selected.get_menu_type(), f"select_{selected.get_menu_type()}",
                             [food.get_name() for food in selected.get_select_option()], index)
               for index, selected in enumerate(boxset.get_box_select_list())]
    return product_detail_page(boxset, "BOX SETS · ชุดอาหาร", options,
                               f"/submit/{boxset_id}", boxset.get_fixed_menu())

@rt("/submit/{boxset_id}", methods=["POST"])
def post(boxset_id: str, select_menu: dict, counter_value: int):
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    
    if isinstance(member,Manager):
        return Redirect("/menu")
    
    select_menu.pop("counter_value", None)
    
    # ดึงข้อมูลเมนูที่เลือก
    selected_foods = [select_menu[key] for key in select_menu]
    
    # ใช้ค่าจำนวนที่ส่งมา
    system.choose_boxset(boxset_id, selected_foods, counter_value)

    return Redirect("/menu")

@rt("/food/{food_id}")
def food_detail(food_id: str):
    food = system.search_food_by_id(food_id)
    if not food:
        return P("Food not found.")
    options = []
    category = "DRINKS · เครื่องดื่ม" if isinstance(food, Drink) else "DESSERTS · ของหวาน" if isinstance(food, Dessert) else "À LA CARTE · อาหารจานเดี่ยว"
    if food.get_select():
        is_drink = isinstance(food, Drink)
        levels = ["ไม่หวาน", "หวานน้อย", "ปกติ", "หวานมาก"] if is_drink else ["ไม่เผ็ด", "เผ็ดน้อย", "เผ็ดมาก", "เผ็ดมากสุดๆ", "เผ็ดนรก"]
        options.append(product_option("ระดับความหวาน" if is_drink else "ระดับความเผ็ด", "select_sweet_level", levels, 0))
    return product_detail_page(food, category, options, f"/submit_food/{food_id}")


@rt("/submit_food/{food_id}", methods=["POST"])
def post_food(food_id: str, select_menu: dict):
    member = session.get_current_user()
    
    if isinstance(member,Manager):
        return Redirect("/menu")
    
    if not member:
        return Redirect("/fail")  # ถ้าไม่มีผู้ใช้ใน session ให้ไปที่หน้าล้มเหลว
    
    # ตรวจสอบข้อมูลจาก select_menu
    counter_value = select_menu.get('counter_value', 1)  # ถ้าไม่มี 'counter_value' ให้ใช้ค่าเริ่มต้นเป็น 1
    level = select_menu.get('select_sweet_level', None)  # ค่าเริ่มต้นเป็น 'ปกติ'
    
    # ส่งข้อมูลไปที่ system.choose_menu
    system.choose_menu(food_id, counter_value, level)
    
    # เปลี่ยนไปที่หน้ารายการเมนูอาหาร
    return Redirect("/menu")  # ✅ เปลี่ยนไปหน้ารายการเมนูอาหาร

@rt("/")
def home_page():
    featured = system.get_boxset_list()[:3]
    if not featured:
        featured = system.get_menu_list()[:3]

    hero_images = [(item.get_picture(), item.get_name()) for item in featured if item.get_picture()]
    slide_count = len(hero_images)
    hero_keyframes = []
    for index in range(slide_count if slide_count > 1 else 0):
        start = index * 100 / slide_count
        hold = (index + .76) * 100 / slide_count
        hero_keyframes.append(
            f"{start:.4f}%, {hold:.4f}% {{ transform:translate3d(-{index * 100}%,0,0); }}")
    hero_keyframes.append(f"100% {{ transform:translate3d(-{slide_count * 100 if slide_count > 1 else 0}%,0,0); }}")

    def featured_card(item):
        href = (f"/boxset/{item.get_boxset_id()}" if isinstance(item, Boxset)
                else f"/food/{item.get_food_id()}")
        return A(
            Div(Span("OUR SERVICE", cls="home-photo-fallback"),
                Img(src=item.get_picture(), alt=item.get_name(), loading="lazy",
                    width="480", height="360", onerror="this.hidden=true"), cls="home-card-photo"),
            Div(H3(item.get_name()),
                Div(Strong(f"฿{item.get_price():,.0f}"), Span("เลือกเมนู ↗"), cls="home-card-bottom"),
                cls="home-card-copy"), href=href, cls="home-card")

    return (
        Title("อร่อยได้ทุกวัน | OUR SERVICE"),
        Style("@keyframes home-slides {" + "".join(hero_keyframes) + "}"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700;800&display=swap');
            body:has(.home-page) { margin:0; background:#faf8f4; }
            .home-page { --red:#c92027; color:#25231f; font-family:'K2D',sans-serif; }
            .home-page * { box-sizing:border-box; }
            .home-page a { text-decoration:none; }
            .home-page h1,.home-page h2,.home-page h3,.home-page p { margin:0; color:inherit; }
            .home-header { background:white; border-bottom:1px solid #eee8de; padding:16px max(24px,calc((100% - 1200px)/2)); }
            .home-header .site-navbar { gap:12px; }
            .home-header button { margin:0; white-space:nowrap; font-family:inherit; }
            .home-header .site-navbar > button:first-child { color:var(--red) !important; font-size:28px !important; padding-left:0 !important; letter-spacing:-1px; }
            .home-header .site-navbar > div { gap:4px !important; }
            .home-order > div { width:100% !important; max-width:100% !important; height:auto !important; min-height:64px; padding:12px 24px !important; gap:24px; background:#25231f !important; flex-wrap:wrap; }
            .home-order h2,.home-order h5 { margin:0 !important; font-size:14px; letter-spacing:.5px; }
            .home-order button { margin:0; font-family:inherit; font-size:14px !important; background:#fff !important; color:var(--red) !important; border-radius:6px; padding:8px 18px !important; }
            .home-shell { max-width:1256px; margin:auto; padding:36px 28px 64px; }
            .home-hero { display:grid; grid-template-columns:1fr 1.08fr; min-height:500px; overflow:hidden; border-radius:20px; background:#f0e9dc; }
            .home-hero-copy { padding:54px 44px; display:flex; flex-direction:column; align-items:flex-start; justify-content:center; }
            .home-eyebrow { color:var(--red) !important; font-size:12px; font-weight:700; letter-spacing:2px; margin-bottom:20px !important; }
            .home-hero h1 { font-size:clamp(38px,4.5vw,64px); font-weight:800; line-height:1.2; letter-spacing:-2px; }
            .home-hero h1 span { color:var(--red); }
            .home-intro { color:#686054 !important; font-size:17px; line-height:1.8; margin-top:22px !important; max-width:360px; }
            .home-actions { display:flex; flex-wrap:wrap; gap:12px; margin-top:30px; }
            .home-primary,.home-secondary { display:inline-flex; align-items:center; justify-content:center; gap:26px; padding:14px 24px; border-radius:7px; font-weight:600; font-size:15px; }
            .home-primary { background:var(--red); color:white !important; }
            .home-secondary { border:1px solid #c7bdae; color:#25231f !important; }
            .home-primary:hover { background:#a71920; }
            .home-secondary:hover { background:#e5dccb; }
            .home-hero-art { position:relative; background:#a71721; min-height:340px; min-width:0; overflow:hidden; }
            .home-hero-track { position:absolute; inset:0; display:flex; transform:translate3d(0,0,0); will-change:transform; animation:home-slides var(--slide-duration) cubic-bezier(.45,0,.2,1) infinite; }
            .home-hero-slide { position:relative; flex:0 0 100%; height:100%; overflow:hidden; }
            .home-hero-art img { width:100%; max-width:none; height:100%; object-fit:cover; object-position:center; display:block; position:absolute; inset:0; }
            .home-hero-label { position:absolute; bottom:22px; left:22px; background:#fff8ec; color:#7a1820; padding:10px 18px; border-radius:6px; font-size:13px; font-weight:600; }
            .home-steps { display:grid; grid-template-columns:repeat(3,1fr); padding:28px 0; border-bottom:1px solid #e3ddd3; margin-bottom:44px; gap:24px; }
            .home-step { display:flex; align-items:center; gap:16px; }
            .home-step > span { font-size:24px; font-weight:700; color:#bcada0; }
            .home-step strong { display:block; font-size:15px; }
            .home-step p { font-size:13px; color:#797168; margin-top:3px; }
            .home-section-title { display:flex; justify-content:space-between; align-items:end; gap:20px; margin-bottom:24px; }
            .home-section-title .home-eyebrow { margin-bottom:8px !important; }
            .home-section-title h2 { font-size:30px; font-weight:700; letter-spacing:-.5px; }
            .home-section-title > a { color:var(--red); font-size:14px; white-space:nowrap; }
            .home-cards { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:22px; }
            .home-card { display:block; overflow:hidden; background:white; border:1px solid #e7e1d8; border-radius:12px; color:#25231f; transition:transform .2s,box-shadow .2s; }
            .home-card:hover { transform:translateY(-4px); box-shadow:0 10px 24px #392a1410; color:#25231f; }
            .home-card-photo { position:relative; aspect-ratio:1.55; background:#f2eee8; display:grid; place-items:center; }
            .home-photo-fallback { color:#ac9d8e; font-weight:700; letter-spacing:2px; font-size:14px; }
            .home-card-photo img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; }
            .home-card-copy { padding:22px; }
            .home-card h3 { font-size:20px; line-height:1.4; }
            .home-card-bottom { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-top:20px; }
            .home-card-bottom strong { color:var(--red); font-size:23px; }
            .home-card-bottom span { font-size:13px; color:#746a60; }
            .home-footer { max-width:1200px; margin:auto; border-top:1px solid #e3ddd3; padding:26px 0; display:flex; justify-content:space-between; gap:18px; color:#84796d; font-size:12px; }
            .home-footer strong { color:var(--red); letter-spacing:1px; }
            .home-page a:focus-visible,.home-page button:focus-visible { outline:3px solid #dc9235; outline-offset:5px; }
            @media(max-width:850px) {
                .home-hero-copy { padding:36px 28px; }
                .home-hero { min-height:440px; }
                .home-header { padding:14px 20px; }
                .home-header .site-navbar { flex-wrap:wrap; gap:0; }
                .home-header .site-navbar > button:first-child { font-size:24px !important; }
                .home-header .site-navbar button { padding:8px 10px !important; font-size:13px !important; }
                .home-footer { margin:0 28px; }
            }
            @media(max-width:600px) {
                .home-shell { padding:20px 18px 36px; }
                .home-header .site-navbar > div { width:100%; justify-content:flex-end; }
                .home-order > div { gap:10px; padding:12px 16px !important; }
                .home-order h5 { font-size:11px; }
                .home-hero { grid-template-columns:1fr; border-radius:12px; }
                .home-hero-copy { padding:32px 24px; }
                .home-hero h1 { font-size:44px; }
                .home-hero-art { min-height:280px; }
                .home-steps { grid-template-columns:1fr; gap:20px; margin-bottom:30px; }
                .home-section-title h2 { font-size:25px; }
                .home-cards { grid-template-columns:1fr; gap:18px; }
                .home-footer { margin:0 18px; flex-wrap:wrap; }
            }
            @media(prefers-reduced-motion:reduce) {
                .home-card { transition:none; }
                .home-hero-track { animation:none; will-change:auto; }
            }
        """),
        Div(
            Div(navbar(), cls="home-header"),
            Div(order_section(), cls="home-order"),
            Main(
                Section(
                    Div(P("GOOD FOOD. GOOD MOOD.", cls="home-eyebrow"),
                        H1("มื้อที่ใช่", Br(), Span("อร่อยได้ทุกวัน")),
                        P("เติมความสุขให้ทุกมื้อ ด้วยเมนูจานโปรดและชุดอิ่มคุ้ม เลือกความอร่อยในแบบคุณได้เลย", cls="home-intro"),
                        Div(A("สั่งอาหารเลย", Span("↗", aria_hidden="true"), href="/selectdelivery", cls="home-primary"),
                            A("สำรวจเมนู", href="/menu", cls="home-secondary"), cls="home-actions"),
                        cls="home-hero-copy"),
                    Div(Div(*[
                            Div(Img(src=src, alt=alt if index < slide_count else "",
                                    fetchpriority="high" if index == 0 else "auto",
                                    onerror="this.hidden=true"), cls="home-hero-slide",
                                aria_hidden="true" if index == slide_count else "false")
                            for index, (src, alt) in enumerate(hero_images + (hero_images[:1] if slide_count > 1 else []))
                        ], cls="home-hero-track", style=f"--slide-duration:{max(slide_count, 1) * 5}s"),
                        Span("ความอร่อย พร้อมให้คุณเลือก", cls="home-hero-label"), cls="home-hero-art"),
                    cls="home-hero", aria_label="เริ่มสั่งอาหาร"),
                Div(*[Div(Span(number), Div(Strong(title), P(description)), cls="home-step")
                      for number, title, description in [
                          ("01", "เลือกเมนูที่ชอบ", "ทั้งจานเดี่ยว ชุดอาหาร และเครื่องดื่ม"),
                          ("02", "เลือกวิธีรับอาหาร", "จัดส่งถึงบ้าน หรือรับเองที่สาขา"),
                          ("03", "พร้อมอิ่มอร่อย", "ตรวจสอบรายการ แล้วชำระเงิน")]], cls="home-steps"),
                Section(Div(Div(P("FIND YOUR FAVORITE", cls="home-eyebrow"), H2("มื้อนี้ กินอะไรดี?")),
                            A("ดูเมนูทั้งหมด →", href="/menu"), cls="home-section-title"),
                        Div(*[featured_card(item) for item in featured], cls="home-cards"),
                        aria_label="เมนูอาหาร"), cls="home-shell"),
            Footer(Strong("OUR SERVICE"), Span("ทุกมื้ออร่อย เริ่มต้นที่นี่"), cls="home-footer"),
            cls="home-page"),
    )

@rt("/menu")
def menu_page():
    member = session.get_current_user()
    categories = [
        ("boxsets", "ชุดอาหาร", "BOX SETS", system.get_boxset_list()),
        ("savory", "อาหารจานเดี่ยว", "À LA CARTE",
         [food for food in system.get_menu_list() if isinstance(food, Savory)]),
        ("desserts", "ของหวาน", "DESSERTS",
         [food for food in system.get_menu_list() if isinstance(food, Dessert)]),
        ("drinks", "เครื่องดื่ม", "DRINKS",
         [food for food in system.get_menu_list() if isinstance(food, Drink)]),
    ]

    def menu_card(item):
        is_boxset = isinstance(item, Boxset)
        href = (f"/boxset/{item.get_boxset_id()}" if is_boxset
                else f"/food/{item.get_food_id()}")
        description = (
            " · ".join(food.get_name() for food in item.get_fixed_menu())
            if is_boxset else
            ("เลือกระดับความหวานได้" if isinstance(item, Drink)
             else "เลือกระดับความเผ็ดได้") if item.get_select() else ""
        )
        return Article(
            A(
                Div(
                    Span("ยังไม่มีรูปภาพ", cls="menu-image-fallback", aria_hidden="true"),
                    Img(src=item.get_picture(), alt=item.get_name(),
                        loading="lazy", decoding="async", width="480", height="388",
                        onerror="this.hidden = true; this.previousElementSibling.hidden = false;",
                        cls="menu-image"),
                    cls="menu-photo",
                ),
                Div(
                    H3(item.get_name()),
                    P(description, cls="menu-description") if description else None,
                    Div(
                        Strong(f"฿{item.get_price():,.0f}", cls="menu-price"),
                        Span("เลือกเมนู", Span(" →", aria_hidden="true"), cls="menu-select"),
                        cls="menu-card-bottom",
                    ),
                    cls="menu-card-content",
                ),
                href=href, cls="menu-card-link",
            ),
            cls="menu-card",
        )

    return (
        Title("เมนูอาหาร | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.menu-page) { margin: 0; background: #fff; }
            main.container:has(.menu-page) { width: 100%; max-width: none; padding: 0; }
            .menu-page {
                --menu-red: #c92027; --menu-ink: #202020; --menu-muted: #666;
                color-scheme: light; background: #fff; color: var(--menu-ink);
                font-family: 'K2D', sans-serif; font-size: 16px; min-height: 100vh;
                --pico-color: #202020; --pico-h1-color: #202020;
                --pico-h2-color: #202020; --pico-h3-color: #202020;
            }
            .menu-page *, .menu-page *::before, .menu-page *::after { box-sizing: border-box; }
            .menu-page a { text-decoration: none; }
            .menu-page a:focus-visible, .menu-page button:focus-visible {
                outline: 3px solid var(--menu-red); outline-offset: 5px;
            }
            .menu-header > div {
                max-width: 1280px; margin-inline: auto; padding: 12px 32px;
                flex-wrap: wrap;
            }
            .menu-header button { margin-bottom: 0; width: auto; font-family: inherit; }
            .menu-header .site-navbar > button:nth-child(2) {
                color: var(--menu-red) !important; font-weight: 700 !important;
            }
            .menu-order { background: #202020; }
            .menu-order > div {
                max-width: 1280px !important; width: 100% !important; height: auto !important;
                min-height: 66px; padding: 12px 32px !important; gap: 20px;
                background: #202020 !important; flex-wrap: wrap;
            }
            .menu-order h2, .menu-order h5 {
                margin: 0 !important; font-size: 15px; font-weight: 500; letter-spacing: .02em;
            }
            .menu-order button {
                width: auto; margin: 0; padding: 8px 18px !important;
                color: #fff !important; background: var(--menu-red) !important;
                border-radius: 3px; font-family: inherit; font-size: 14px !important;
            }
            .menu-shell { max-width: 1216px; margin: auto; padding: 0 32px 80px; }
            .menu-intro { padding: 48px 0 28px; }
            .menu-eyebrow {
                margin: 0 0 12px; color: var(--menu-red); font-size: 12px;
                font-weight: 700; letter-spacing: .16em;
                display: flex; align-items: center; gap: 10px;
            }
            .menu-eyebrow::before { content: ''; width: 26px; height: 3px; background: var(--menu-red); }
            .menu-intro h1 { margin: 0 0 10px; font-size: clamp(32px, 4vw, 48px); line-height: 1.25; }
            .menu-intro > p:last-child { margin: 0; color: var(--menu-muted); font-size: 16px; }
            .menu-categories {
                position: sticky; top: 0; z-index: 5; display: flex; justify-content: flex-start;
                gap: 32px; overflow-x: auto; background: #fff;
                border-bottom: 1px solid #dedbd6; margin-bottom: 36px;
                scrollbar-width: thin;
            }
            .menu-categories a {
                display: inline-flex; flex-shrink: 0; align-items: center; gap: 9px;
                padding: 17px 0; color: var(--menu-muted); font-weight: 600;
                border-bottom: 3px solid transparent;
            }
            .menu-categories a:hover, .menu-categories a[aria-current="location"] {
                color: var(--menu-red); border-bottom-color: var(--menu-red);
            }
            .menu-categories a span { color: #777; font-size: 12px; font-weight: 400; }
            .menu-section { scroll-margin-top: 96px; margin: 0 0 48px; }
            .menu-section-heading {
                display: flex; align-items: baseline; flex-wrap: wrap; gap: 12px;
                margin-bottom: 20px;
            }
            .menu-section-heading h2 { margin: 0; font-size: 26px; font-weight: 700; }
            .menu-section-heading span { color: var(--menu-muted); font-size: 11px; letter-spacing: .12em; }
            .menu-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 28px 24px; }
            .menu-card {
                min-width: 0; margin: 0; padding: 0; overflow: hidden;
                border: 1px solid #e5e2dd; border-radius: 4px; background: white; box-shadow: none;
            }
            .menu-card-link { height: 100%; display: flex; flex-direction: column; color: inherit; }
            .menu-card-link:hover { color: inherit; }
            .menu-card:has(a:hover) { border-color: #bbb5ac; }
            .menu-photo { position: relative; aspect-ratio: 1.65; background: #f5f4f0; overflow: hidden; }
            .menu-image {
                position: relative; display: block; width: 100%; height: 100%;
                object-fit: contain; padding: 12px; transition: transform .18s ease;
            }
            .menu-image[hidden] { display: none; }
            .menu-image-fallback { display: none; position: absolute; inset: 0; place-items: center; color: #777; font-size: 14px; }
            .menu-photo:has(.menu-image[hidden]) .menu-image-fallback { display: grid; }
            .menu-card-link:hover .menu-image { transform: scale(1.035); }
            .menu-card-content { flex: 1; display: flex; flex-direction: column; padding: 20px; }
            .menu-card h3 { margin: 0; font-size: 19px; line-height: 1.5; font-weight: 600; }
            .menu-description { margin: 7px 0 0; font-size: 13px; line-height: 1.65; color: var(--menu-muted); }
            .menu-card-bottom { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-top: auto; padding-top: 22px; }
            .menu-price { font-size: 21px; font-weight: 700; font-variant-numeric: tabular-nums; }
            .menu-select { color: var(--menu-red); font-size: 14px; font-weight: 600; }
            .menu-card-link:hover .menu-select { text-decoration: underline; text-underline-offset: 4px; }
            .menu-empty { color: var(--menu-muted); padding: 24px 0; border-top: 1px solid #e5e2dd; }
            .menu-end { border-top: 1px solid #dedbd6; padding-top: 24px; display: flex; justify-content: space-between; gap: 20px; font-size: 13px; }
            .menu-end span { color: var(--menu-muted); }
            .menu-end a { color: var(--menu-ink); }
            @media (max-width: 850px) {
                .menu-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
                .menu-header > div { padding: 12px 20px; }
                .menu-header > div > button:first-child { font-size: 26px !important; padding-left: 0 !important; }
                .menu-header > div > div { gap: 0 !important; }
                .menu-header button { padding: 10px !important; font-size: 13px !important; }
            }
            @media (max-width: 540px) {
                .menu-shell { padding: 0 20px 48px; }
                .menu-intro { padding-top: 32px; }
                .menu-intro > p:last-child { font-size: 14px; }
                .menu-header > div > div { width: 100%; justify-content: flex-end; }
                .menu-order > div { padding: 14px 20px !important; gap: 10px; }
                .menu-order h2, .menu-order h5 { font-size: 12px; }
                .menu-categories { gap: 24px; margin-bottom: 28px; }
                .menu-categories a { font-size: 14px; }
                .menu-grid { grid-template-columns: 1fr; gap: 20px; }
                .menu-photo { aspect-ratio: 1.9; }
                .menu-section-heading h2 { font-size: 23px; }
                .menu-section { margin-bottom: 36px; }
            }
            @media (prefers-reduced-motion: reduce) {
                .menu-image { transition: none; }
                .menu-card-link:hover .menu-image { transform: none; }
            }
        """),
        Div(
            Div(managebar() if isinstance(member, Manager) else navbar(), cls="menu-header"),
            Div(order_section(), cls="menu-order"),
            Div(
                Header(
                    P("OUR SERVICE / MENU", cls="menu-eyebrow"),
                    H1("เมนูของเรา"),
                    P("เลือกชุดโปรด หรือจัดมื้ออร่อยในแบบของคุณ"),
                    cls="menu-intro", id="menu-top",
                ),
                Nav(
                    *[A(label, Span(str(len(items))), href=f"#{key}",
                        aria_current="location" if index == 0 else None)
                      for index, (key, label, english, items) in enumerate(categories)],
                    cls="menu-categories", aria_label="หมวดหมู่อาหาร",
                ),
                *[Section(
                    Div(H2(label), Span(english), cls="menu-section-heading"),
                    Div(*[menu_card(item) for item in items], cls="menu-grid")
                    if items else P("ยังไม่มีเมนูในหมวดนี้", cls="menu-empty"),
                    id=key, cls="menu-section",
                  ) for key, label, english, items in categories],
                Footer(Span("OUR SERVICE"), A("กลับด้านบน ↑", href="#menu-top"), cls="menu-end"),
                cls="menu-shell",
            ),
            cls="menu-page",
        ),
        Script("""
            (() => {
                const page = document.querySelector('.menu-page');
                if (!page) return;
                const links = [...page.querySelectorAll('.menu-categories a')];
                const sections = [...page.querySelectorAll('.menu-section')];
                const update = () => {
                    const active = sections.filter(section => section.getBoundingClientRect().top <= 140).pop() || sections[0];
                    links.forEach(link => {
                        if (link.hash === '#' + active.id) link.setAttribute('aria-current', 'location');
                        else link.removeAttribute('aria-current');
                    });
                };
                const controller = new AbortController();
                window.addEventListener('scroll', () => {
                    if (!page.isConnected) { controller.abort(); return; }
                    update();
                }, { passive: true, signal: controller.signal });
                update();
            })();
        """),
    )


@rt("/basket/quantity", methods=["POST"])
def update_basket_quantity(item_id: str, change: int, coupon_code: str = ""):
    member = session.get_current_user()
    if not member:
        return Redirect('/fail')
    if isinstance(member, Manager):
        return Redirect('/menu')
    basket = member.get_current_basket()
    if basket:
        basket.change_quantity(item_id, change)
    return Redirect('/basket?' + urlencode({'coupon_code': coupon_code}) if coupon_code else '/basket')


@rt("/basket")
def view_basket(coupon_code: str = None):
    member = session.get_current_user()
    if not member:
        return Redirect('/fail')
    if isinstance(member, Manager):
        return Redirect('/menu')

    items, total_price, discount_applied, discount_include = member.view_basket(coupon_code)
    coupon_code = member.get_current_basket().get_coupon_code()
    quantity = sum(int(item['quantity']) for item in items)

    def basket_item(item):
        product = item['name']
        details = []
        if isinstance(product, Drink) and product.get_select():
            details.append(P(f"ความหวาน: {product.get_select()}", cls="basket-muted"))
        elif isinstance(product, Savory) and product.get_select():
            details.append(P(f"ความเผ็ด: {product.get_select()}", cls="basket-muted"))
        elif isinstance(product, Boxset):
            details.append(P(f"เมนูที่เลือก: {product.get_selected_menu()}", cls="basket-muted"))
        return Article(
            Div(Span("ไม่มีรูปภาพ", cls="basket-image-fallback"),
                Img(src=product.get_picture(), alt=product.get_name(), loading="lazy",
                    onerror="this.hidden=true", width="112", height="112"), cls="basket-photo"),
            Div(H3(product.get_name()), *details,
                P(f"฿{product.get_price():,.2f} / รายการ", cls="basket-muted"),
                Form(
                    Input(type="hidden", name="item_id", value=item['item_id']),
                    Input(type="hidden", name="coupon_code", value=coupon_code),
                    Button("−", type="submit", name="change", value="-1",
                           aria_label=f"ลดจำนวน {product.get_name()}"),
                    Span(str(item['quantity']), aria_label="จำนวนสินค้า", cls="basket-quantity"),
                    Button("+", type="submit", name="change", value="1",
                           aria_label=f"เพิ่มจำนวน {product.get_name()}"),
                    action="/basket/quantity", method="post", cls="basket-stepper"),
                cls="basket-item-info"),
            Strong(f"฿{product.get_price() * int(item['quantity']):,.2f}", cls="basket-line-price"),
            cls="basket-item",
        )

    content = Div(
        Section(
            Div(H2("รายการอาหาร"), Span(f"{quantity} ชิ้น", cls="basket-muted"), cls="basket-section-title"),
            *[basket_item(item) for item in items],
            A("← เลือกเมนูเพิ่ม", href="/menu", cls="basket-more"),
            cls="basket-items", aria_label="รายการในตะกร้า",
        ),
        Aside(
            H2("สรุปคำสั่งซื้อ"),
            Form(Label("โค้ดส่วนลด", fr="basket-coupon"),
                 Div(Input(type="text", id="basket-coupon", name="coupon_code", placeholder="กรอกโค้ดส่วนลด",
                           value=coupon_code, autocomplete="off"),
                     Button("ใช้โค้ด", type="submit"), cls="basket-coupon-row"),
                 P("ใช้โค้ดส่วนลดแล้ว" if discount_applied else "ไม่พบโค้ดส่วนลดนี้",
                   cls="basket-coupon-message", role="status") if coupon_code else None,
                 action="/basket", method="get", cls="basket-coupon"),
            Div(Span("ยอดรวมสินค้า"), Span(f"฿{total_price:,.2f}"), cls="basket-total-row"),
            Div(Span("ส่วนลด"), Span(f"−฿{discount_applied:,.2f}"), cls="basket-total-row basket-discount"),
            Div(Strong("ยอดรวมสุทธิ"), Strong(f"฿{discount_include:,.2f}"), cls="basket-total-row basket-grand-total"),
            A("ดำเนินการชำระเงิน →", href="/payment", cls="basket-primary"),
            cls="basket-summary", aria_label="สรุปคำสั่งซื้อ",
        ), cls="basket-layout",
    ) if items else Section(
        Div(Span("0"), cls="basket-empty-icon", aria_hidden="true"),
        P("พร้อมสำหรับมื้ออร่อยหรือยัง?", cls="basket-eyebrow"),
        H2("ตะกร้าของคุณยังว่างอยู่"),
        P("เลือกเมนูโปรด แล้วกลับมาสั่งความอร่อยได้ที่นี่", cls="basket-muted"),
        A("เลือกเมนูอาหาร →", href="/menu", cls="basket-primary"), cls="basket-empty",
    )
    return (
        Title("ตะกร้าของคุณ | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.basket-page) { margin:0; background:#fff; }
            main.container:has(.basket-page) { width:100%; max-width:none; padding:0; }
            .basket-page { color-scheme:light; background:#fff; color:#202020; font-family:'K2D',sans-serif;
                font-size:16px; min-height:100vh; --pico-color:#202020; --pico-h1-color:#202020;
                --pico-h2-color:#202020; --pico-h3-color:#202020; }
            .basket-page *, .basket-page *::before, .basket-page *::after { box-sizing:border-box; }
            .basket-page a { color:#c92027; text-decoration:none; }
            .basket-page button, .basket-page input { font-family:inherit; }
            .basket-page :is(a,button,input):focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            .basket-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .basket-header button { width:auto; margin:0; }
            .basket-header .site-navbar > div > button:first-child { color:#c92027 !important; font-weight:700 !important; }
            .basket-order { background:#202020; }
            .basket-order > div { width:100% !important; max-width:1280px !important; height:auto !important;
                min-height:66px; margin:auto !important; padding:12px 32px !important; gap:20px;
                flex-wrap:wrap; background:#202020 !important; }
            .basket-order h2, .basket-order h5 { margin:0 !important; font-size:15px; }
            .basket-order button { width:auto; margin:0; background:#c92027 !important; color:#fff !important;
                font-size:14px !important; border-radius:3px; }
            .basket-shell { max-width:1216px; margin:auto; padding:40px 32px 72px; }
            .basket-eyebrow { color:#c92027; font-size:12px; font-weight:700; letter-spacing:.12em; margin:0 0 12px; }
            .basket-intro { margin-bottom:36px; }
            .basket-intro h1 { font-size:clamp(32px,4vw,48px); margin:0 0 10px; line-height:1.3; }
            .basket-muted { color:#707070; font-size:14px; margin:0; }
            .basket-layout { display:grid; grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr); gap:40px; align-items:start; }
            .basket-page h2 { font-size:22px; margin:0; }
            .basket-section-title { display:flex; align-items:center; justify-content:space-between; gap:12px; padding-bottom:20px; border-bottom:1px solid #e5e2dd; }
            .basket-item { display:grid; grid-template-columns:112px minmax(0,1fr) auto; gap:20px; align-items:center;
                margin:0; padding:24px 0; background:transparent; border-bottom:1px solid #e5e2dd; border-radius:0; box-shadow:none; }
            .basket-photo { position:relative; width:112px; height:112px; background:#f5f3ef; border-radius:4px; overflow:hidden; }
            .basket-photo img { position:relative; width:100%; height:100%; object-fit:contain; background:#f5f3ef; }
            .basket-photo img[hidden] { display:none; }
            .basket-image-fallback { position:absolute; inset:0; display:grid; place-items:center; color:#707070; font-size:12px; }
            .basket-item h3 { font-size:18px; line-height:1.5; margin:0 0 6px; }
            .basket-item-info { overflow-wrap:anywhere; }
            .basket-item-info p { margin-bottom:6px; }
            .basket-stepper { display:inline-flex; align-items:center; margin:8px 0 0; gap:0;
                border:1px solid #d9d5cf; border-radius:4px; background:#fff; }
            .basket-stepper button { width:40px; height:40px; margin:0; padding:0; border:0;
                border-radius:3px; background:#fff; color:#202020; font-size:20px; }
            .basket-stepper button:hover { background:#f5f3ef; }
            .basket-quantity { min-width:36px; text-align:center; font-size:14px; }
            .basket-line-price { font-size:18px; white-space:nowrap; }
            .basket-more { display:inline-block; margin-top:24px; font-size:14px; font-weight:600; }
            .basket-more:hover { text-decoration:underline; }
            .basket-summary { padding:28px; background:#f8f7f4; border:1px solid #e5e2dd; border-top:3px solid #c92027; border-radius:4px; }
            .basket-coupon { margin:12px 0; padding-bottom:12px; border-bottom:1px solid #dedbd6; }
            .basket-coupon label { color:#202020; font-size:14px; margin-bottom:8px; }
            .basket-summary { min-width:0; }
            .basket-coupon-row { display:grid; grid-template-columns:minmax(0,1fr) auto; gap:8px; }
            .basket-coupon-row input { min-width:0; width:100%; margin:0; height:46px; padding:10px 12px;
                border:1px solid #d9d5cf; border-radius:3px; background:#fff; color:#202020; font-size:14px; }
            .basket-coupon-row button { width:auto; white-space:nowrap; margin:0; padding:10px 16px; border:1px solid #202020;
                border-radius:3px; background:#202020; color:#fff; font-size:14px; }
            .basket-coupon-message { margin:10px 0 0; font-size:13px; color:#c92027; }
            .basket-total-row { display:flex; justify-content:space-between; gap:16px; margin-bottom:14px; font-size:14px; font-variant-numeric:tabular-nums; }
            .basket-discount { color:#c92027; }
            .basket-grand-total { border-top:1px solid #dedbd6; padding-top:20px; margin:20px 0 24px; font-size:20px; }
            .basket-page .basket-primary { display:block; padding:15px 20px; background:#c92027; color:#fff; border-radius:4px; text-align:center; font-size:16px; font-weight:600; }
            .basket-page .basket-primary:hover { background:#a8171d; }
            .basket-empty { padding:56px 24px; text-align:center; background:#f8f7f4; border:1px solid #e5e2dd; border-radius:4px; }
            .basket-empty h2 { margin-bottom:12px; font-size:clamp(24px,3vw,30px); }
            .basket-empty .basket-primary { max-width:260px; margin:28px auto 0; }
            .basket-empty-icon { position:relative; display:grid; place-items:center; width:68px; height:60px; margin:12px auto 32px;
                border:3px solid #c92027; border-radius:5px 5px 16px 16px; color:#c92027; font-size:24px; }
            .basket-empty-icon::before { content:''; position:absolute; width:30px; height:18px; top:-18px; border:3px solid #c92027; border-bottom:0; border-radius:14px 14px 0 0; }
            @media(max-width:850px) {
                .basket-layout { grid-template-columns:1fr; gap:32px; }
                .basket-header > div { padding:12px 20px; }
                .basket-header .site-navbar > button:first-child { font-size:26px !important; padding-left:0 !important; }
                .basket-header .site-navbar > div { gap:0 !important; flex-wrap:wrap; }
                .basket-header button { padding:10px !important; font-size:13px !important; }
            }
            @media(max-width:540px) {
                .basket-shell { padding:28px 20px 48px; }
                .basket-header .site-navbar > div { width:100%; justify-content:flex-end; }
                .basket-order > div { padding:14px 20px !important; gap:10px; }
                .basket-order h2, .basket-order h5 { font-size:12px; }
                .basket-item { grid-template-columns:80px minmax(0,1fr); gap:12px; }
                .basket-photo { width:80px; height:80px; }
                .basket-line-price { grid-column:2; }
                .basket-summary { padding:22px; }
                .basket-empty { padding:44px 20px; }
            }
        """),
        Div(Div(navbar(), cls="basket-header"), Div(order_section(), cls="basket-order"),
            Div(Header(P("OUR SERVICE / BASKET", cls="basket-eyebrow"), H1("ตะกร้าของคุณ"),
                       P("ตรวจสอบรายการโปรด ก่อนสั่งความอร่อย", cls="basket-muted"), cls="basket-intro"),
                content, cls="basket-shell"), cls="basket-page"),
    )



def fulfillment_page(title, subtitle, content, selection=False):
    return (
        Title(title + " | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.fulfillment-page) { margin:0; background:#fff; }
            main.container:has(.fulfillment-page) { width:100%; max-width:none; padding:0; }
            .fulfillment-page { color-scheme:light; min-height:100vh; background:#fff; color:#202020;
                font-family:'K2D',sans-serif; font-size:16px; --pico-color:#202020;
                --pico-h1-color:#202020; --pico-h2-color:#202020; --pico-h3-color:#202020; }
            .fulfillment-page *, .fulfillment-page *::before, .fulfillment-page *::after { box-sizing:border-box; }
            .fulfillment-page :is(button,input,textarea) { font-family:inherit; }
            .fulfillment-page a { color:#c92027; text-decoration:none; }
            .fulfillment-page :is(a,button,input,textarea):focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            .fulfillment-header { border-bottom:1px solid #e5e2dd; }
            .fulfillment-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .fulfillment-header button { width:auto; margin:0; }
            .fulfillment-banner { background:#202020; color:#fff; padding:18px 24px; text-align:center; font-size:14px; }
            .fulfillment-shell { max-width:1120px; margin:auto; padding:40px 32px 72px; }
            .fulfillment-back { display:inline-block; font-size:14px; margin-bottom:28px; }
            .fulfillment-back:hover { text-decoration:underline; }
            .fulfillment-eyebrow { color:#c92027; font-size:12px; font-weight:700; letter-spacing:.12em; margin:0 0 12px; }
            .fulfillment-intro { margin-bottom:32px; }
            .fulfillment-intro h1 { font-size:clamp(28px,4vw,44px); line-height:1.3; margin:0 0 12px; }
            .fulfillment-muted { color:#707070; font-size:14px; line-height:1.8; margin:0; }
            .fulfillment-methods { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px; }
            .fulfillment-page .fulfillment-method { display:flex; flex-direction:column; align-items:flex-start;
                padding:32px; gap:14px; background:#f8f7f4; border:1px solid #e5e2dd; border-radius:4px; color:#202020; }
            .fulfillment-method:hover { border-color:#c92027; background:#fff5f3; }
            .fulfillment-page h2 { font-size:22px; margin:0 0 12px; }
            .fulfillment-method h2 { margin:0; }
            .fulfillment-icon { display:grid; place-items:center; width:56px; height:56px; background:#fff;
                border:1px solid #e5e2dd; border-radius:4px; color:#c92027; font-size:26px; }
            .fulfillment-action { color:#c92027; font-weight:600; margin-top:12px; }
            .fulfillment-layout { display:grid; grid-template-columns:minmax(0,1.4fr) minmax(0,1fr); gap:32px; align-items:start; }
            .fulfillment-panel { min-width:0; padding:28px; background:#f8f7f4; border:1px solid #e5e2dd; border-radius:4px; }
            .fulfillment-panel form { margin:24px 0 0; }
            .fulfillment-page label { display:block; color:#202020; font-size:15px; font-weight:500; margin-bottom:10px; }
            .fulfillment-page :is(input,textarea) { width:100%; margin:0 0 12px; padding:14px 16px; background:#fff;
                color:#202020; border:1px solid #ccc; border-radius:4px; font-size:16px; box-shadow:none; }
            .fulfillment-page textarea { min-height:150px; resize:vertical; }
            .fulfillment-page :is(input,textarea)::placeholder { color:#777; }
            .fulfillment-page .fulfillment-primary, .fulfillment-page .select-button { display:block; width:100%; margin:20px 0 0;
                padding:14px 20px; background:#c92027; border:1px solid #c92027; border-radius:4px;
                color:#fff; font-size:16px; font-weight:600; text-align:center; cursor:pointer; }
            .fulfillment-page .fulfillment-primary:hover, .fulfillment-page .select-button:hover { background:#a8171d; }
            .fulfillment-selected { border-top:3px solid #c92027; padding-top:24px; min-width:0; }
            .fulfillment-selection { margin:20px 0; padding:20px; background:#f8f7f4; font-size:15px; overflow-wrap:anywhere; }
            .fulfillment-page .branch-card { padding:20px; margin-top:16px; background:#fff; border:1px solid #e5e2dd; border-radius:4px; }
            .fulfillment-page .branch-title { font-size:18px; margin:0 0 8px; }
            .fulfillment-page .branch-address { font-size:14px; color:#707070; margin:0; }
            .fulfillment-page #results { margin-top:20px; font-size:14px; }
            .fulfillment-page .no-branch { color:#c92027; }
            @media(max-width:760px) {
                .fulfillment-header > div { padding:12px 20px; }
                .fulfillment-header .site-navbar > button:first-child { font-size:26px !important; padding-left:0 !important; }
                .fulfillment-header .site-navbar > div { gap:0 !important; flex-wrap:wrap; }
                .fulfillment-header button { padding:10px !important; font-size:13px !important; }
                .fulfillment-shell { padding:28px 20px 48px; }
                .fulfillment-methods, .fulfillment-layout { grid-template-columns:1fr; gap:20px; }
                .fulfillment-page .fulfillment-method, .fulfillment-panel { padding:24px; }
            }
            @media(max-width:480px) {
                .fulfillment-header .site-navbar > div { width:100%; justify-content:flex-end; }
            }
        """),
        Div(Div(navbar(), cls="fulfillment-header"),
            Div("อร่อยได้ในแบบคุณ · รับที่ร้าน หรือจัดส่งถึงบ้าน", cls="fulfillment-banner"),
            Div(A("← กลับหน้าหลัก" if selection else "← เปลี่ยนช่องทางรับอาหาร",
                  href="/" if selection else "/selectdelivery", cls="fulfillment-back"),
                Header(P("OUR SERVICE / " + ("ORDER OPTIONS" if selection else "ORDER DETAILS"), cls="fulfillment-eyebrow"),
                       H1(title), P(subtitle, cls="fulfillment-muted"), cls="fulfillment-intro"),
                content, cls="fulfillment-shell"), cls="fulfillment-page"),
    )


@rt('/selectdelivery')
def order_type():
    return fulfillment_page("เลือกช่องทางการรับออเดอร์", "เลือกวิธีรับอาหารที่สะดวกสำหรับคุณ แล้วไปเลือกเมนูโปรดกัน",
        Div(
            A(Span("⌂", cls="fulfillment-icon", aria_hidden="true"), H2("รับที่ร้าน"),
              P("ค้นหาสาขาใกล้คุณ แล้วรับอาหารด้วยตัวเองที่ร้าน", cls="fulfillment-muted"),
              Span("เลือกสาขาที่รับอาหาร →", cls="fulfillment-action"), href="/pickup", cls="fulfillment-method"),
            A(Span("→", cls="fulfillment-icon", aria_hidden="true"), H2("เดลิเวอรี่"),
              P("ส่งความอร่อยถึงมือคุณ เพียงระบุที่อยู่จัดส่ง", cls="fulfillment-muted"),
              Span("กรอกที่อยู่จัดส่ง →", cls="fulfillment-action"), href="/delivery", cls="fulfillment-method"),
            cls="fulfillment-methods"), selection=True)


@rt('/pickup')
def pickup_page():
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    if not isinstance(member.get_order_type(), PickUp):
        member.add_order_type(PickUp())
    selected = member.get_order_type().get_selected_branch()
    return fulfillment_page("เลือกสาขาที่รับอาหาร", "ค้นหาสาขาด้วยรหัสไปรษณีย์ แล้วเลือกสาขาที่คุณสะดวกไปรับ",
        Div(Section(H2("ค้นหาสาขา"), P("กรอกรหัสไปรษณีย์ในพื้นที่ที่ต้องการรับอาหาร", cls="fulfillment-muted"),
                Form(Label("รหัสไปรษณีย์", fr="postcode"),
                     Input(id="postcode", name="postcode", placeholder="เช่น 10150", required=True,
                           inputmode="numeric", pattern="[0-9]{5}", maxlength="5", autocomplete="postal-code"),
                     Button("ค้นหาสาขา", type="submit", cls="fulfillment-primary"),
                     hx_get="/search", hx_target="#results", hx_trigger="submit, input changed delay:300ms from:input"),
                Div(id="results", aria_live="polite"), cls="fulfillment-panel"),
            Aside(H2("สาขาที่เลือก"), P("เลือกสาขาจากผลการค้นหา", cls="fulfillment-muted"),
                  Div(B(f"{selected['district']} ({selected['address']})" if selected else "ยังไม่ได้เลือกสาขา"), id="selected_branch", cls="fulfillment-selection", aria_live="polite"),
                  A("เลือกเมนูอาหาร →", href="/menu", cls="fulfillment-primary"), cls="fulfillment-selected"),
            cls="fulfillment-layout"))


@rt('/delivery')
def delivery_page():
    member = session.get_current_user()
    if not member:
        return Redirect("/fail")
    if not isinstance(member.get_order_type(), Delivery):
        member.add_order_type(Delivery())
    return fulfillment_page("ที่อยู่จัดส่ง", "ระบุที่อยู่ให้ครบถ้วน เพื่อให้เราจัดส่งอาหารถึงคุณ",
        Div(Section(H2("รายละเอียดที่อยู่"), P("กรอกที่อยู่พร้อมรหัสไปรษณีย์ของคุณ", cls="fulfillment-muted"),
                Form(Label("ที่อยู่จัดส่ง", fr="delivery_address"),
                     Textarea(member.get_order_type().get_address() or "", id="delivery_address", name="address", required=True, rows="5",
                              placeholder="บ้านเลขที่ หมู่บ้าน / อาคาร ถนน แขวง / ตำบล เขต / อำเภอ จังหวัด และรหัสไปรษณีย์",
                              autocomplete="street-address", aria_describedby="delivery-hint"),
                     P("ระบุชื่ออาคาร ชั้น หรือจุดสังเกตเพิ่มเติม เพื่อให้ค้นหาที่อยู่ได้ง่ายขึ้น", id="delivery-hint", cls="fulfillment-muted"),
                     Button("ยืนยันที่อยู่และเลือกเมนู →", type="submit", cls="fulfillment-primary"),
                     method="post", action="/submit_address"),
                Div(id="address_confirmation", aria_live="polite"), cls="fulfillment-panel"),
            Aside(H2("จัดส่งถึงหน้าประตู"),
                  P("ตรวจสอบบ้านเลขที่และรหัสไปรษณีย์ก่อนยืนยัน จากนั้นเลือกอาหารที่คุณต้องการได้เลย", cls="fulfillment-muted"),
                  A("รับอาหารที่ร้านแทน →", href="/pickup", cls="fulfillment-back", style="margin-top:24px"),
                  cls="fulfillment-selected"), cls="fulfillment-layout"))


@rt('/submit_address', methods=['POST'])
def submit_address(address: str):
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/fail')
    delivery = Delivery()
    delivery.set_address(address.strip())
    if not address.strip() or delivery.get_branch() is None:
        return fulfillment_page("ตรวจสอบที่อยู่จัดส่ง", "กรุณาระบุที่อยู่พร้อมรหัสไปรษณีย์ในพื้นที่ให้บริการ",
            Div(P(address), A("กลับไปแก้ไขที่อยู่", href="/delivery")))
    member.add_order_type(delivery)
    return Redirect('/menu')

@rt('/select_delivery')
def select_delivery():
    delivery = session.get_current_user().get_order_type()
    return Titled("Delivery Information",
        H3(f"Delivery Address: {delivery.get_address()}"),
        Button("Done", onclick="window.location.href='/menu';", cls = "done-button"),
    )

@rt('/search')
def search(postcode: Optional[str] = None):
    if not postcode or not postcode.strip().isdigit():
        return B("กรุณากรอกรหัสไปรษณีย์เป็นตัวเลข")
    result = system.search_branches(postcode.strip())
    return Div(result)


@rt('/fail')
def fail_page():
    return (
        Title("กรุณาเข้าสู่ระบบ | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.fail-page) { margin:0; background:#fff; }
            main.container:has(.fail-page) { width:100%; max-width:none; padding:0; }
            .fail-page { color-scheme:light; min-height:100vh; background:#fff; color:#202020;
                font-family:'K2D',sans-serif; font-size:16px;
                --pico-color:#202020; --pico-h1-color:#202020; }
            .fail-page *, .fail-page *::before, .fail-page *::after { box-sizing:border-box; }
            .fail-page button { font-family:inherit; }
            .fail-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .fail-header button { width:auto; margin:0; }
            .fail-order { background:#202020; }
            .fail-order > div { max-width:1280px !important; width:100% !important;
                height:auto !important; min-height:66px; margin:auto; padding:12px 32px !important;
                gap:20px; background:#202020 !important; flex-wrap:wrap; }
            .fail-order h2, .fail-order h5 { margin:0 !important; font-size:15px; font-weight:500; }
            .fail-order button { width:auto; margin:0; padding:8px 18px !important;
                background:#c92027 !important; color:#fff !important; border-radius:3px; font-size:14px !important; }
            .fail-shell { max-width:680px; margin:auto; padding:48px 24px 72px; }
            .fail-back { color:#666; font-size:14px; text-decoration:none; }
            .fail-card { margin-top:24px; padding:48px 36px; text-align:center;
                border:1px solid #dedbd6; border-top:4px solid #c92027; border-radius:4px; background:#f8f7f4; }
            .fail-icon { position:relative; width:72px; height:72px; margin:0 auto 24px;
                border:1px solid #e5e2dd; border-radius:50%; background:#fff; }
            .fail-icon::before { content:''; position:absolute; width:22px; height:20px;
                top:16px; left:24px; border:3px solid #c92027; border-radius:12px 12px 0 0; }
            .fail-icon::after { content:''; position:absolute; width:32px; height:25px;
                top:32px; left:19px; border:3px solid #c92027; border-radius:4px; background:#fff; }
            .fail-eyebrow { margin:0 0 12px; color:#c92027; font-size:12px; font-weight:700; letter-spacing:.16em; }
            .fail-card h1 { margin:0 0 16px; font-size:clamp(28px,4vw,36px); line-height:1.35; }
            .fail-description { margin:0; color:#666; font-size:16px; line-height:1.8; }
            .fail-actions { display:flex; justify-content:center; gap:12px; margin-top:28px; }
            .fail-actions a { flex:1; padding:13px 20px; border:1px solid #c92027; border-radius:4px;
                color:#c92027; background:#fff; font-weight:600; text-decoration:none; }
            .fail-actions .fail-primary { background:#c92027; color:#fff; }
            .fail-actions a:hover { background:#fff5f3; }
            .fail-actions .fail-primary:hover { background:#a8171d; border-color:#a8171d; }
            .fail-page a:focus-visible, .fail-page button:focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            @media (max-width:640px) {
                .fail-header > div { padding:12px 16px; gap:4px; }
                .fail-header .site-navbar > button:first-child { font-size:26px !important; padding:8px !important; }
                .fail-header .site-navbar > div { width:100%; justify-content:center; gap:8px !important; }
                .fail-header button { padding:8px 12px !important; }
                .fail-order > div { padding:16px !important; gap:12px; }
                .fail-shell { padding:28px 16px 48px; }
                .fail-card { padding:32px 20px; }
                .fail-actions { flex-direction:column; }
            }
        """),
        Div(
            Div(navbar(), cls="fail-header"),
            Div(order_section(), cls="fail-order"),
            Main(
                A("← กลับหน้าหลัก", href="/", cls="fail-back"),
                Div(
                    Div(cls="fail-icon", aria_hidden="true"),
                    P("OUR SERVICE / MEMBER", cls="fail-eyebrow"),
                    H1("กรุณาเข้าสู่ระบบก่อน"),
                    P("เข้าสู่ระบบเพื่อดำเนินการต่อและสั่งเมนูโปรดของคุณ",
                      Br(), "หากยังไม่มีบัญชี สามารถสมัครสมาชิกได้เลย", cls="fail-description"),
                    Div(
                        A("เข้าสู่ระบบ", href="/login", cls="fail-primary"),
                        A("สมัครสมาชิก", href="/register"),
                        cls="fail-actions",
                    ),
                    cls="fail-card",
                ),
                cls="fail-shell",
            ),
            cls="fail-page",
        ),
    )


@rt('/select_branch', methods=['POST'])
def select_branch(district: str, address: str):
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/fail')
    pickup = PickUp()
    pickup.set_branch({"district": district, "address": address})
    if pickup.get_branch() is None:
        return B("ไม่พบสาขาที่เลือก กรุณาค้นหาสาขาอีกครั้ง")
    member.add_order_type(pickup)
    return B(f"{district} ({address})")

def auth_field(label, name, placeholder, input_type="text", autocomplete="off"):
    return Div(
        Label(label, For=name),
        Input(type=input_type, id=name, name=name, placeholder=placeholder,
              autocomplete=autocomplete, required=True),
        cls="auth-field",
    )


def auth_page(register=False):
    title = "สร้างบัญชีผู้ใช้" if register else "เข้าสู่ระบบ"
    fields = []
    if register:
        fields.extend([
            auth_field("ชื่อ", "name", "ชื่อจริง", autocomplete="given-name"),
            auth_field("นามสกุล", "surname", "นามสกุล", autocomplete="family-name"),
            auth_field("เบอร์โทรศัพท์", "tel_number", "หมายเลขโทรศัพท์", "tel", "tel"),
            auth_field("อีเมล", "email", "อีเมลของคุณ", "email", "email"),
        ])
    fields.extend([
        auth_field("ชื่อผู้ใช้", "username", "กรอกชื่อผู้ใช้", autocomplete="username"),
        auth_field("รหัสผ่าน", "password", "กรอกรหัสผ่าน", "password",
                   "new-password" if register else "current-password"),
    ])
    return (
        Title(f"{title} | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.auth-page) { margin:0; background:#fff; }
            main.container:has(.auth-page) { width:100%; max-width:none; padding:0; }
            .auth-page { color-scheme:light; min-height:100vh; background:#fff;
                color:#202020; font-family:'K2D',sans-serif; font-size:16px;
                --pico-color:#202020; --pico-h1-color:#202020;
                --pico-primary:#c92027; --pico-primary-focus:rgba(201,32,39,.18); }
            .auth-page *, .auth-page *::before, .auth-page *::after { box-sizing:border-box; }
            .auth-page button, .auth-page input { font-family:inherit; }
            .auth-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .auth-header button { width:auto; margin:0; }
            .auth-order { background:#202020; }
            .auth-order > div { max-width:1280px !important; width:100% !important;
                height:auto !important; min-height:66px; margin:auto; padding:12px 32px !important;
                gap:20px; background:#202020 !important; flex-wrap:wrap; }
            .auth-order h2, .auth-order h5 { margin:0 !important; font-size:15px; font-weight:500; }
            .auth-order button { width:auto; margin:0; padding:8px 18px !important;
                background:#c92027 !important; color:#fff !important; border-radius:3px; font-size:14px !important; }
            .auth-shell { max-width:680px; margin:auto; padding:48px 24px 72px; }
            .auth-back { color:#666; font-size:14px; text-decoration:none; }
            .auth-card { margin-top:24px; padding:36px; border:1px solid #dedbd6;
                border-top:4px solid #c92027; border-radius:4px; background:#fff; }
            .auth-eyebrow { margin:0 0 12px; color:#c92027; font-size:12px; font-weight:700; letter-spacing:.16em; }
            .auth-card h1 { margin:0 0 12px; font-size:clamp(28px,4vw,36px); line-height:1.3; }
            .auth-subtitle { margin:0 0 28px; color:#666; font-size:15px; }
            .auth-form { margin:0; }
            .auth-fields { display:grid; gap:20px; }
            .auth-register .auth-fields { grid-template-columns:repeat(2,minmax(0,1fr)); }
            .auth-field label { display:block; margin:0 0 8px; color:#202020; font-size:14px; font-weight:600; }
            .auth-field input { width:100%; height:48px; margin:0; padding:12px 14px;
                border:1px solid #ccc; border-radius:4px; background:#fff; color:#202020; font-size:16px; box-shadow:none; }
            .auth-field input::placeholder { color:#777; }
            .auth-field input:focus { border-color:#c92027; box-shadow:0 0 0 3px rgba(201,32,39,.12); }
            .auth-submit { width:100%; margin:28px 0 0; padding:13px 20px;
                background:#c92027; border:1px solid #c92027; border-radius:4px; color:#fff; font-size:16px; font-weight:700; }
            .auth-submit:hover { background:#a71920; border-color:#a71920; }
            .auth-switch { margin:24px 0 0; padding-top:24px; border-top:1px solid #eee;
                color:#666; text-align:center; font-size:14px; }
            .auth-switch a { color:#c92027; font-weight:600; text-underline-offset:4px; }
            .auth-page a:focus-visible, .auth-page button:focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            @media (max-width:640px) {
                .auth-header > div { padding:12px 16px; gap:4px; }
                .auth-header .site-navbar > button:first-child { font-size:26px !important; padding:8px !important; }
                .auth-header .site-navbar > div { width:100%; justify-content:center; gap:8px !important; }
                .auth-header button { padding:8px 12px !important; }
                .auth-order > div { padding:16px !important; gap:12px; }
                .auth-shell { padding:28px 16px 48px; }
                .auth-card { padding:24px 20px; }
                .auth-register .auth-fields { grid-template-columns:1fr; }
            }
        """),
        Div(
            Div(navbar(), cls="auth-header"),
            Div(order_section(), cls="auth-order"),
            Div(
                A("← กลับหน้าหลัก", href="/", cls="auth-back"),
                Div(
                    P("OUR SERVICE / MEMBER", cls="auth-eyebrow"),
                    H1(title),
                    P("สมัครสมาชิกเพื่อเริ่มสั่งเมนูโปรดของคุณ" if register else
                      "ยินดีต้อนรับกลับมา เข้าสู่ระบบเพื่อสั่งเมนูโปรดของคุณ", cls="auth-subtitle"),
                    Form(
                        Div(*fields, cls="auth-fields"),
                        Button("สร้างบัญชี" if register else "เข้าสู่ระบบ", type="submit", cls="auth-submit"),
                        method="post", action="/register/submit" if register else "/login/submit", cls="auth-form",
                    ),
                    P("มีบัญชีอยู่แล้ว? " if register else "ยังไม่มีบัญชี? ",
                      A("เข้าสู่ระบบ" if register else "สมัครสมาชิก", href="/login" if register else "/register"),
                      cls="auth-switch"),
                    cls="auth-card",
                ),
                cls="auth-shell",
            ),
            cls="auth-page auth-register" if register else "auth-page",
        ),
    )


@rt("/login")
def get():
    return auth_page()


@rt("/register")
def get():
    return auth_page(register=True)


@rt("/login/submit")
def post(username: str, password: str):
    return system.handle_authentication("login", username=username, password=password)

@rt("/register/submit")
def post(name: str, surname: str, tel_number: str, email: str, username: str, password: str):
    return system.handle_authentication("register", name, surname, tel_number, email, username, password)

def checkout_page(title, subtitle, content, qr=False, summary=False):
    return (
        Title(f"{title} | OUR SERVICE"),
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=K2D:wght@400;500;600;700&display=swap');
            body:has(.checkout-page) { margin:0; background:#fff; }
            main.container:has(.checkout-page) { width:100%; max-width:none; padding:0; }
            .checkout-page { color-scheme:light; min-height:100vh; background:#fff; color:#202020;
                font-family:'K2D',sans-serif; font-size:16px; --pico-color:#202020;
                --pico-h1-color:#202020; --pico-h2-color:#202020; --pico-h3-color:#202020; }
            .checkout-page *, .checkout-page *::before, .checkout-page *::after { box-sizing:border-box; }
            .checkout-page a { color:#c92027; text-decoration:none; }
            .checkout-page button { font-family:inherit; }
            .checkout-page :is(a,button):focus-visible { outline:3px solid #c92027; outline-offset:4px; }
            .checkout-header > div { max-width:1280px; margin:auto; padding:12px 32px; flex-wrap:wrap; }
            .checkout-header button { width:auto; margin:0; }
            .checkout-order { background:#202020; }
            .checkout-order > div { width:100% !important; max-width:1280px !important; height:auto !important;
                min-height:66px; margin:auto !important; padding:12px 32px !important; gap:20px;
                flex-wrap:wrap; background:#202020 !important; }
            .checkout-order h2, .checkout-order h5 { margin:0 !important; font-size:15px; }
            .checkout-order button { width:auto; margin:0; background:#c92027 !important; color:#fff !important;
                font-size:14px !important; border-radius:3px; }
            .checkout-shell { max-width:1216px; margin:auto; padding:40px 32px 72px; }
            .checkout-back { display:inline-block; font-size:14px; font-weight:600; margin-bottom:28px; }
            .checkout-back:hover { text-decoration:underline; }
            .checkout-eyebrow { color:#c92027; font-size:12px; font-weight:700; letter-spacing:.12em; margin:0 0 12px; }
            .checkout-intro { margin-bottom:32px; }
            .checkout-intro h1 { font-size:clamp(30px,4vw,48px); line-height:1.3; margin:0 0 12px; }
            .checkout-muted { color:#707070; font-size:14px; margin:0; line-height:1.8; }
            .checkout-page h2 { font-size:22px; margin:0 0 12px; }
            .checkout-methods { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:24px; }
            .checkout-page .checkout-method { display:flex; flex-direction:column; align-items:flex-start; gap:12px;
                padding:32px; border:1px solid #e5e2dd; border-top:3px solid #c92027; border-radius:4px;
                background:#f8f7f4; color:#202020; transition:background .15s,border-color .15s; }
            .checkout-method:hover { background:#fff5f3; border-color:#c92027; }
            .checkout-method h2 { margin:4px 0 0; }
            .checkout-icon { display:grid; place-items:center; width:64px; height:56px; background:#fff;
                border:1px solid #e5e2dd; border-radius:4px; color:#c92027; font-weight:700; font-size:18px; }
            .checkout-method-action { margin-top:16px; color:#c92027; font-weight:600; }
            .checkout-qr-layout { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:48px; align-items:start; }
            .checkout-qr-panel { padding:32px; background:#f8f7f4; border:1px solid #e5e2dd; border-radius:4px; text-align:center; }
            .checkout-qr-frame { width:min(100%,280px); margin:24px auto; padding:20px; background:#fff; border:1px solid #e5e2dd; border-radius:4px; }
            .checkout-qr-frame img { display:block; width:100%; height:auto; aspect-ratio:1; object-fit:contain; }
            .checkout-summary { border-top:3px solid #c92027; padding-top:28px; min-width:0; }
            .checkout-amount { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap;
                gap:12px; padding:20px 0; margin-bottom:24px; border-bottom:1px solid #e5e2dd; }
            .checkout-amount strong { font-size:32px; color:#c92027; font-variant-numeric:tabular-nums; }
            .checkout-instructions { padding-left:24px; margin:16px 0 28px; color:#707070; font-size:15px; }
            .checkout-instructions li { padding-left:6px; margin-bottom:12px; }
            .checkout-page .checkout-primary { display:block; width:100%; margin:0; padding:15px 20px;
                border:1px solid #c92027; background:#c92027; color:#fff; border-radius:4px; font-size:16px; font-weight:600; }
            .checkout-primary:hover { background:#a8171d; border-color:#a8171d; }
            .checkout-secondary { display:block; text-align:center; margin-top:18px; font-size:14px; }
            .checkout-secondary:hover { text-decoration:underline; }
            @media(max-width:850px) {
                .checkout-header > div { padding:12px 20px; }
                .checkout-header .site-navbar > button:first-child { font-size:26px !important; padding-left:0 !important; }
                .checkout-header .site-navbar > div { gap:0 !important; flex-wrap:wrap; }
                .checkout-header button { padding:10px !important; font-size:13px !important; }
                .checkout-qr-layout { gap:24px; }
            }
            @media(max-width:600px) {
                .checkout-shell { padding:28px 20px 48px; }
                .checkout-header .site-navbar > div { width:100%; justify-content:flex-end; }
                .checkout-order > div { padding:14px 20px !important; gap:10px; }
                .checkout-order h2, .checkout-order h5 { font-size:12px; }
                .checkout-methods, .checkout-qr-layout { grid-template-columns:1fr; }
                .checkout-methods { gap:16px; }
                .checkout-page .checkout-method, .checkout-qr-panel { padding:24px; }
            }
            @media(prefers-reduced-motion:reduce) { .checkout-method { transition:none; } }
        """),
        Div(Div(navbar(), cls="checkout-header"), Div(order_section(), cls="checkout-order"),
            Div(A("← กลับหน้าหลัก" if summary else "← เลือกวิธีชำระเงิน" if qr else "← กลับไปตะกร้า", href="/" if summary else "/payment" if qr else "/basket", cls="checkout-back"),
                Header(P("OUR SERVICE / " + ("ORDER SUMMARY" if summary else "QR PAYMENT" if qr else "PAYMENT"), cls="checkout-eyebrow"),
                       H1(title), P(subtitle, cls="checkout-muted"), cls="checkout-intro"),
                content, cls="checkout-shell"), cls="checkout-page"),
    )


def fulfillment_redirect(member):
    order_type = member.get_order_type()
    if isinstance(order_type, Delivery):
        if not order_type.get_address() or order_type.get_branch() is None:
            return Redirect('/delivery')
    elif isinstance(order_type, PickUp):
        if order_type.get_branch() is None:
            return Redirect('/pickup')
    else:
        return Redirect('/selectdelivery')
    return None


@rt('/payment')
def payment_page():
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/menu' if isinstance(member, Manager) else '/fail')
    redirect = fulfillment_redirect(member)
    if redirect is not None:
        return redirect
    return checkout_page("วิธีการชำระเงิน", "เลือกวิธีชำระเงินที่สะดวกสำหรับคุณ",
        Div(
            A(Span("QR", cls="checkout-icon", aria_hidden="true"), H2("ชำระด้วย QR Code"),
              P("สแกน QR Code เพื่อชำระเงิน", cls="checkout-muted"),
              Span("ชำระด้วย QR Code →", cls="checkout-method-action"), href="/QR", cls="checkout-method"),
            A(Span("CARD", cls="checkout-icon", aria_hidden="true"), H2("ชำระด้วยบัตรเครดิต"),
              P("กรอกข้อมูลบัตรเพื่อดำเนินการชำระเงิน", cls="checkout-muted"),
              Span("ชำระด้วยบัตรเครดิต →", cls="checkout-method-action"), href="/account_num", cls="checkout-method"),
            cls="checkout-methods"),
    )


@rt('/QR')
def qr_payment_page():
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/menu' if isinstance(member, Manager) else '/fail')
    redirect = fulfillment_redirect(member)
    if redirect is not None:
        return redirect
    return checkout_page("ชำระด้วย QR Code", "ตรวจสอบยอดชำระก่อนยืนยันคำสั่งซื้อ",
        Div(
            Section(P("QR CODE", cls="checkout-eyebrow"), H2("สแกนเพื่อชำระเงิน"),
                Div(Img(src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/QR_code_for_mobile_English_Wikipedia.svg/330px-QR_code_for_mobile_English_Wikipedia.svg.png",
                        alt="QR Code ตัวอย่าง", width="240", height="240"), cls="checkout-qr-frame"),
                P("QR Code ตัวอย่างสำหรับสาธิต", cls="checkout-muted"), cls="checkout-qr-panel"),
            Section(H2("รายละเอียดการชำระเงิน"),
                Div(Span("ยอดชำระทั้งหมด"), Strong(f"฿{member.get_current_basket().calculate_payable_total():,.2f}"), cls="checkout-amount"),
                H2("ขั้นตอนการชำระเงิน"),
                Ol(Li("เปิดแอปธนาคาร แล้วเลือกสแกน QR Code"),
                   Li("ตรวจสอบยอดเงินและข้อมูลผู้รับก่อนชำระ"),
                   Li("เมื่อชำระแล้ว กดปุ่มยืนยันด้านล่าง"), cls="checkout-instructions"),
                Form(Button("ชำระเงินเสร็จสิ้น →", type="submit", cls="checkout-primary"),
                     method="post", action=f'/total/order/{member.get_id}'),
                A("เปลี่ยนวิธีชำระเงิน", href="/payment", cls="checkout-secondary"), cls="checkout-summary"),
            cls="checkout-qr-layout"), qr=True,
    )


@rt('/account_num')
def get():
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/menu' if isinstance(member, Manager) else '/fail')
    redirect = fulfillment_redirect(member)
    if redirect is not None:
        return redirect

    grid_content = [
        navbar(),  # Navbar
        order_section(),  # Order Section
    ]

    grid_content.append(Container(
        Style("""
            @import url('https://fonts.googleapis.com/css2?family=TH+Sarabun:wght@400;500;700&display=swap');

            html, body {
                background: #ffffff;
                min-height: 100vh;
                margin: 0;
                padding: 0;
                font-family: 'TH Sarabun', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                text-align: center;
                overflow-x: hidden;
            }

            .register-title {
                font-size: 42px;
                font-weight: 800;
                color: #000000;
                margin-top: 30px;
            }

            .register-form {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                margin-top: 20px;
            }

            .input-field {
                width: 400px;
                height: 50px;
                font-size: 18px;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid #ddd;
                background-color: #ffffff;
                color: #333;
                box-sizing: border-box;
            }

            .input-field::placeholder {
                color: #333;
            }

            .input-field:focus {
                background-color: #f0f0f0;
                border: 1px solid #000;
            }

            .register-submit-button {
                width: 200px;
                height: 50px;
                font-size: 20px;
                font-weight: bold;
                text-align: center;
                border: none;
                background: #28a745;
                color: white;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.2);
                transition: all 0.3s ease-in-out;
                margin-top: 20px;
            }

            .register-submit-button:hover {
                background: #218838;
                transform: scale(1.02);
            }

            .register-submit-button:active {
                transform: scale(0.95);
            }

            .label {
                color: #3d3c3c;
                text-align: left;
                display: block;
                width: 100%;
                padding-left: 10px;
                box-sizing: border-box;
                margin-top: -10px;
            }
        """),
        H1("ชำระเงินด้วยบัตรเครดิต", cls="register-title"),
        P(f"Price: ฿{member.get_current_basket().calculate_payable_total():,.2f}"),
        Form(
            Div(
                Label("ชื่อ:", cls="label"),
                Input(type="text", name="first_name", placeholder="ชื่อ", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("นามสกุล:", cls="label"),
                Input(type="text", name="last_name", placeholder="นามสกุล", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("เลขบัตรเครดิต:", cls="label"),
                Input(type="text", name="credit_card", placeholder="เลขบัตรเครดิต", required=True, cls="input-field"),
                cls="register-form"
            ),
            Div(
                Label("CVV:", cls="label"),
                Input(type="password", name="cvv", placeholder="CVV", required=True, cls="input-field"),
                cls="register-form"
            ),
            Button('ชำระเงินเสร็จสิ้น', type="submit", cls="register-submit-button"),
            method="post",
            action=f"/total/order/{member.get_id}",
            cls="register-form"
        )
    ))

    return grid_content


@rt('/total/order/{member_id}')
def post(member_id: str):
    
    return Redirect('/summary')

@rt('/summary')
def summary_page():
    member = session.get_current_user()
    if not isinstance(member, Member):
        return Redirect('/menu' if isinstance(member, Manager) else '/fail')
    order_type = member.get_order_type()
    redirect = fulfillment_redirect(member)
    if redirect is not None:
        return redirect
    if not member.get_current_basket().check_empty():
        return Redirect('/basket')

    user_info, items, total_price, _, discount_applied = system.summary_order()
    branch = order_type.get_branch()
    rider = None
    delivery_details = []
    if isinstance(order_type, Delivery):
        assigned_rider = system.find_free_rider(order_type)
        rider = None if assigned_rider == "Busy" else assigned_rider
        delivery_details = [
            Div(Span("ที่อยู่จัดส่ง"), P(order_type.get_address()), cls="summary-detail summary-wide"),
            Div(Span("ผู้จัดส่ง"), P(rider.get_account_name() if rider else "กำลังรอไรเดอร์ว่าง"), cls="summary-detail"),
        ]
    order = member.create_order_history(rider)
    system.manage_stock(branch)

    rows = []
    for item in items:
        product, quantity = item["name"], int(item["quantity"])
        details = []
        if isinstance(product, (Drink, Savory)) and product.get_select() is not None:
            label = "ระดับความหวาน" if isinstance(product, Drink) else "ระดับความเผ็ด"
            details.append(P(f"{label}: {product.get_select()}", cls="checkout-muted"))
        if isinstance(product, Boxset):
            details.append(P(f"เมนูที่เลือก: {product.get_selected_menu()}", cls="checkout-muted"))
        rows.append(Li(
            Div(H3(product.get_name()), *details,
                P(f"฿{float(product.get_price()):,.2f} / ชิ้น", cls="checkout-muted")),
            Span(f"× {quantity}", cls="summary-quantity"),
            Strong(f"฿{float(product.get_price()) * quantity:,.2f}", cls="summary-line-price"),
            cls="summary-item"))

    return checkout_page("สรุปคำสั่งซื้อ", "ขอบคุณที่ใช้บริการ ตรวจสอบรายการอาหารและรายละเอียดการรับอาหารได้ด้านล่าง",
        Div(
            Style("""
                .summary-receipt { display:flex; align-items:center; justify-content:space-between; gap:16px;
                    flex-wrap:wrap; padding:20px 24px; margin-bottom:32px; background:#202020; color:#fff; border-radius:4px; }
                .summary-receipt p { margin:0; color:#fff; font-size:14px; }
                .summary-receipt strong { font-size:22px; font-variant-numeric:tabular-nums; }
                .summary-layout { display:grid; grid-template-columns:minmax(0,1.6fr) minmax(0,1fr); gap:40px; align-items:start; }
                .summary-layout > * { min-width:0; }
                .summary-customer { border-top:1px solid #e5e2dd; padding-top:28px; margin-top:32px; }
                .summary-details { display:grid; grid-template-columns:1fr 1fr; gap:20px 28px; margin-top:24px; }
                .summary-detail > span { color:#707070; font-size:13px; }
                .summary-detail p { margin:6px 0 0; line-height:1.7; overflow-wrap:anywhere; }
                .summary-wide { grid-column:1 / -1; }
                .summary-items { padding:0; margin:8px 0 0; list-style:none; }
                .summary-items .summary-item { list-style:none; display:grid; grid-template-columns:minmax(0,1fr) auto auto;
                    align-items:start; gap:20px; padding:22px 0; border-bottom:1px solid #e5e2dd; margin:0; }
                .summary-item h3 { font-size:18px; margin:0 0 6px; overflow-wrap:anywhere; }
                .summary-item p { overflow-wrap:anywhere; }
                .summary-quantity { color:#707070; font-size:14px; white-space:nowrap; }
                .summary-line-price { font-size:16px; font-variant-numeric:tabular-nums; white-space:nowrap; }
                .summary-totals { padding:28px; background:#f8f7f4; border:1px solid #e5e2dd; border-top:3px solid #c92027; border-radius:4px; }
                .summary-price-row { display:flex; justify-content:space-between; gap:16px; margin:20px 0; font-size:14px; }
                .summary-discount { color:#c92027; }
                .summary-totals .checkout-amount { border-top:1px solid #e5e2dd; margin-top:24px; padding:24px 0; }
                .summary-totals .checkout-primary { text-align:center; }
                @media(max-width:850px) { .summary-layout { grid-template-columns:1fr; gap:28px; } }
                @media(max-width:600px) {
                    .summary-details { grid-template-columns:1fr; }
                    .summary-totals { padding:24px; }
                    .summary-items .summary-item { grid-template-columns:minmax(0,1fr) auto; gap:8px 16px; }
                    .summary-line-price { grid-column:2; }
                    .summary-item > div { grid-row:span 2; }
                }
            """),
            Div(Div(P("หมายเลขคำสั่งซื้อ"), Strong(f"#{order.get_order_id()}")),
                P("จัดส่งถึงที่" if isinstance(order_type, Delivery) else "รับอาหารที่สาขา"), cls="summary-receipt"),
            Div(
                Div(Section(H2("รายการอาหาร"), P(f"ทั้งหมด {sum(int(item['quantity']) for item in items)} ชิ้น", cls="checkout-muted"),
                        Ul(*rows, cls="summary-items")),
                    Section(H2("ข้อมูลการรับอาหาร"),
                        Div(Div(Span("ชื่อผู้สั่ง"), P(f"{user_info[0]} {user_info[1]}"), cls="summary-detail"),
                            Div(Span("เบอร์โทรศัพท์"), P(user_info[3]), cls="summary-detail"),
                            Div(Span("สาขาที่ให้บริการ"), P(branch.get_branch_address()), cls="summary-detail summary-wide"),
                            *delivery_details, cls="summary-details"), cls="summary-customer")),
                Aside(H2("สรุปยอดคำสั่งซื้อ"),
                    Div(Span("ยอดรวมรายการอาหาร"), Span(f"฿{float(total_price) + float(discount_applied):,.2f}"), cls="summary-price-row"),
                    Div(Span("ส่วนลด"), Span(f"−฿{float(discount_applied):,.2f}"), cls="summary-price-row summary-discount"),
                    Div(Span("ยอดรวมสุทธิ"), Strong(f"฿{float(total_price):,.2f}"), cls="checkout-amount"),
                    A("สั่งอาหารเพิ่ม →", href="/neworder", cls="checkout-primary"),
                    A("กลับหน้าหลัก", href="/", cls="checkout-secondary"), cls="summary-totals"),
                cls="summary-layout"),
        ), summary=True,
    )


@rt("/neworder")
def get():
    member = session.get_current_user()
    member.make_new_order()
    return Redirect("/menu")


@rt("/account")
def get(): 
    grid_content = []
    unique_accounts = set()  # ใช้เซ็ตเพื่อลบค่าซ้ำ

    for account in system.get_member_list():
        account_tuple = (account.get_account_name(), account.get_account_surname(), account.get_email())

        if account_tuple not in unique_accounts:
            unique_accounts.add(account_tuple)
            grid_content.append(
                Card(
                    P(account_tuple[0]),
                    P(account_tuple[1]),
                    P(account_tuple[2])
                )
            )

    return Container(Grid(*grid_content))

@rt("/manager")
def get():
    grid_content = [ managebar()
]
    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    ))

    grid_content.append(
    Div(
        # พื้นหลังสี่เหลี่ยม
        Div(
            # รูปภาพ (อยู่ซ้าย)
            Img(
                id="image",
                src="https://www.kfc.co.th/static/media/empty_cart.32f17a45.png",
                style={
                    "width": "200px",  # กำหนดขนาดรูป
                    "height": "200px",
                    "object-fit": "contain",  # ป้องกันภาพผิดสัดส่วน
                    "margin-right": "20px"  # เว้นระยะระหว่างรูปกับข้อความ
                }
            ),
            # ข้อความ (อยู่ขวา)
            Div(
                H3("WELCOME MANAGER!", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "24px",
                    "margin": "0"
                }),
                P("OUR SERVICE IS FOR CUSTOMERS.", style={
                    "color": "white",  # ตัวอักษรสีขาว
                    "font-size": "16px",
                    "margin-top": "5px"
                }),
                style={
                    "display": "flex",
                    "flex-direction": "column",  # ให้ข้อความอยู่เป็นแนวตั้ง
                    "justify-content": "center"  # จัดให้อยู่ตรงกลางแนวตั้ง
                }
            ),
            style={
                "display": "flex",
                "align-items": "center",  # จัดให้รูปและข้อความอยู่ตรงกลางแนวตั้ง
                "background": "#ff0000",  # สีพื้นหลัง (สีแดง)
                "padding": "20px",  # เพิ่มระยะห่างภายใน
                "border-radius": "10px",  # ขอบมน
                "width": "60%",  # กำหนดความกว้างของกล่อง
                "margin": "auto",  # จัดให้อยู่ตรงกลางของหน้าจอ
                "box-shadow": "0px 4px 10px rgba(0,0,0,0.2)"  # เพิ่มเงาให้ดูสวยงาม
            }
        ),
        style={
            "display": "flex",
            "justify-content": "center",  # จัดให้อยู่กลางหน้าจอ
            "align-items": "center",
            "height": "100vh",  # ให้เต็มจอแนวตั้ง
            "background": "#f4f4f4"  # สีพื้นหลังของหน้าจอ
        }
    )
)
    return grid_content

@rt("/delete_item/{item_id}/{item_type}")
def delete_item(item_id: str, item_type: str):
    
    member = session.get_current_user()
    if not isinstance(member,Manager):
        return Redirect("/fail")  # กรณีไม่ได้ล็อกอิน
    system.delete_item_by_id(item_id, item_type, member) 
    return Redirect("/manage_menu") 
    

@rt("/manage_menu")
def get():
    menu = system.get_boxset_list()
    
    # สร้าง Grid ของ Boxset แต่ละอัน
    grid_content = [
    managebar()
]

    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
                "background": "none",
                "border": "none",
                "color": "red",
                "font-size": "24px",
                "cursor": "pointer",
                "padding": "10px 20px",
            }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
            "margin": "0",
            "padding": "0",
            "box-sizing": "border-box",
        }
    ))
    grid_content.append(
        Div(
            H2("Manage Individual Menu", style={"text-align": "center", "margin-bottom": "20px"}),
            H2("Boxset", style={"text-align": "center", "margin-bottom": "20px"}),
            style={"width": "100%"}
        )
    )
    # ใช้ Grid Layout เพื่อจัดเรียงการ์ดให้สวย
    boxset_grid = Grid(
        *[
            Card(
                H3(boxset.get_name(), style={"color": "black", "font-size": "20px", "margin-bottom": "10px"}),
                P(f"Price: {boxset.get_price()} THB", style={"color": "#666", "font-size": "16px"}),
                P(f"Main menu: {', '.join([food.get_name() for food in boxset.get_fixed_menu()])}",
                  style={"color": "#444", "font-size": "14px"}),

                # ปุ่ม Delete
                A(
                    Button("Delete", style={
                        "background": "red",
                        "color": "white",
                        "border": "none",
                        "padding": "10px 20px",
                        "cursor": "pointer",
                        "border-radius": "5px"
                    }),
                    href=f"/delete_item/{boxset.get_boxset_id()}/boxset"
                ),

                style={
                    "background-color": "white",
                    "border": "1px solid #ddd",
                    "border-radius": "10px",
                    "padding": "20px",
                    "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                    "display": "flex",
                    "flex-direction": "column",
                    "align-items": "center",
                    "gap": "10px",
                    "text-align": "center",
                    "width": "250px"
                }
            ) for boxset in menu
        ],
        style={
            "display": "grid",
            "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",
            "gap": "20px",
            "padding": "20px",
            "justify-content": "center"
        }
    )

    grid_content.append(boxset_grid)
    

    menu_type = [Savory, Dessert, Drink]

    for type in menu_type:
        menu_in_type = []

        grid_content.append(H2(f"{type.__name__} Menu", style={"text-align": "center", "margin-bottom": "20px"}))

        for menu in system.get_menu_list():
            if isinstance(menu, type):
                menu_in_type.append(menu)
    
        menu_grid = Grid(
            *[
                Card(
                    H3(food.get_name(), style={"text-align": "center", "margin-bottom": "20px"}),
                    P(f"Price: {food.get_price()} THB", style={"color": "#666", "font-size": "16px"}),

                    # ปุ่ม Delete
                    A(
                        Button("Delete", style={
                            "background": "red",
                            "color": "white",
                            "border": "none",
                            "padding": "10px 20px",
                            "cursor": "pointer",
                            "border-radius": "5px"
                        }), 
                        href=f"/delete_item/{food.get_food_id()}/food"
                    ),

                    style={
                        "background-color": "white",
                        "border": "1px solid #ddd",
                        "border-radius": "10px",
                        "padding": "20px",
                        "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                        "display": "flex",
                        "flex-direction": "column",
                        "align-items": "center",
                        "gap": "10px",
                        "text-align": "center",
                        "width": "250px"
                    }
                ) for food in menu_in_type
            ],
            style={
                "display": "grid",
                "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))",
                "gap": "20px",
                "padding": "20px",
                "justify-content": "center"
            }
        )

        grid_content.append(menu_grid)

    return Container(*grid_content)

@rt("/restore/menu/{menu_id}")
def restore_menu(menu_id: str):
    member = session.get_current_user()
    if not isinstance(member,Manager):
        return Redirect("/fail")  # กรณีไม่ได้ล็อกอิน

    result = system.restore_item(menu_id, member)
    return result  # กลับไปที่หน้าจัดการเมนู



@rt("/restore_delete_menu")
def get():
    menu = system.get_delete_menu() or []  # ป้องกันกรณี None
    delete_boxset = [item for item in menu if isinstance(item, Boxset)]
    delete_menu = [item for item in menu if isinstance(item, Food)]

    grid_content = [managebar()]

    # คำเตือน
    grid_content.append(Div(
        H3("PLEASE BE CAREFUL", style={
            "color": "red",
            "font-size": "24px",
            "padding": "10px 20px",
        }),
        style={
            "background-color": "black",
            "color": "white",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            "height": "10vh",
            "width": "99vw",
        }
    ))
    grid_content.append(
        Div(
            H2("Manage Individual Menu", style={"text-align": "center", "margin-bottom": "20px"}),
            H2("Boxset", style={"text-align": "center", "margin-bottom": "20px"}),
            style={"width": "100%"}
        )
    )
    # Grid ของ Boxset
    boxset_grid = Grid(
        *[
            Card(
                H3(boxset.get_name(), style={"font-size": "20px"}),
                P(f"Price: {boxset.get_price()} THB"),
                P(f"Main menu: {', '.join([food.get_name() for food in (boxset.get_fixed_menu() or [])])}"),
                A(
                    Button("Restore", style={"background": "green", "color": "white", "padding": "10px"}),
                    href=f"/restore/menu/{boxset.get_boxset_id()}"
                ),
                style={"border": "1px solid #ddd", "padding": "20px", "text-align": "center"}
            ) for boxset in delete_boxset
        ],
        style={"display": "grid", "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))"}
    )

    grid_content.append(boxset_grid)

    # แสดงเมนูแต่ละประเภท
    menu_type = [Savory, Dessert, Drink]
    for type in menu_type:
        menu_in_type = [food for food in delete_menu if isinstance(food, type)]
        
        if menu_in_type:
            grid_content.append(H2(f"{type.__name__} Menu"))

            menu_grid = Grid(
                *[
                    Card(
                        H3(food.get_name()),
                        P(f"Price: {food.get_price()} THB"),
                        A(
                            Button("Restore", style={"background": "green", "color": "white"}),
                            href=f"/restore/menu/{food.get_food_id()}"
                        ),
                        style={"border": "1px solid #ddd", "padding": "20px", "text-align": "center"}
                    ) for food in menu_in_type
                ],
                style={"display": "grid", "grid-template-columns": "repeat(auto-fill, minmax(250px, 1fr))"}
            )
            grid_content.append(menu_grid)

    return Container(*grid_content)

def Card(*children, **kwargs):
    return Div(*children, **kwargs)

def Container(*children, **kwargs):
    return Div(*children, **kwargs)

def Grid(*children, **kwargs):
    return Div(*children, **kwargs)



serve()