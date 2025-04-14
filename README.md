Right now I'm trying to implement checkout. 

### **Steps in the Checkout Process**

shopping cart > billing info > shipping info > shipping method > preview order > payment > confirmation

#### a. **Validate the Cart**
   - Ensure the cart contains valid items (e.g., products exist, quantities are correct).
   - Check if the items are in stock.

#### a.1 **Validate Discounts**
    - Make sure that the discount codes are valid

#### a.2 **Check Promotions**
    - Check if the cart qualifies for getting a promotion or something like that

#### b. **Calculate Totals**
   - Compute the total cost of the order, including:
     - Subtotal (sum of item prices).
     - Taxes (based on location or product type).
     - Shipping fees (if applicable).
   - Return these details to the frontend for confirmation.

#### c. **Process Payment**
   - Integrate with a payment gateway (e.g., Stripe, PayPal, Zelle).
   - Handle payment authorization and capture.
   - Ensure the payment is successful before proceeding. Handle payment confirmation differently based on the method.

#### d. **Create the Order**
   - Once payment is successful:
     - Create an order in the database.
     - Deduct inventory for the purchased items.
     - Add the cart items to the order
     - Save the Shipping Address
     - Associate the order with the user.

#### e. **Send Confirmation**
   - Send an order confirmation email or notification to the user.
   - Return the order details to the frontend.


---

### **Frontend Integration**
   - The frontend sends the cart and payment details to the `POST /checkout` endpoint.
   - The backend processes the request and returns the order confirmation or an error message.
#### There should be a section at the top saying express checkout. 
   - In this section we should have other checkout options like PayPal, Google Pay, Apple Pay or anything else. 
#### After these we should 

---

Nice blog on How to design a checkout flow:
https://www.bolt.com/thinkshop/ecommerce-checkout-process-flow



- CI numero de cedula
- telefono
- 4 numeros de la referenci
