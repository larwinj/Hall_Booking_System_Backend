# 📱 User Flow Documentation

**Project:** Hall Booking System  
**Version:** 2.0 (Updated)  
**Last Updated:** November 15, 2025  
**Status:** Current with 4-Role Architecture

---

## 🎯 Overview

This document details the complete user flow for all **4 user roles** in the Hall Booking System:
- 👤 **Guest** - Read-only browsing
- 👥 **Customer** - Full booking capabilities
- 🏢 **Moderator/Vendor** - Venue & booking management
- 🔑 **Admin** - System administration & analytics

---

## 👤 GUEST USER FLOW

### Guest Access & Navigation

**1. User Visits Website**
- Guest lands on home page
- No authentication required
- Can browse available halls

**2. Browse Hall Categories**
- View hall categories (Small, Medium, Large)
- Browse halls under each category
- View basic hall information

**3. View Hall Details**
- Click on hall to see details:
  - Seating capacity
  - Available amenities (projectors, WiFi, etc.)
  - Cost per hour
  - Photo gallery
  - Customer reviews & ratings

**4. View Availability (Read-only)**
- Check slot availability from 8 AM to 8 PM
- See booked slots marked as unavailable
- See free slots marked as available
- View no availability message if all slots booked

**5. Authentication Required**
- Cannot proceed without login
- Redirected to login page
- Option to register new account

---

## 👥 CUSTOMER USER FLOW

### Phase 1: Authentication

**1. User Visits Website**
- Guest lands on home page
- Can browse halls without login

**2. User Registration (Sign Up)**
- Fills registration form:
  - Email address
  - Password (minimum 8 characters)
  - Confirm password
  - Accept terms & conditions
- **System validates:**
  - Email format (RFC 5321)
  - Password strength
  - Email uniqueness
- On success → Redirected to login page
- Confirmation email sent (optional)

**3. User Login**
- Enters email & password
- **System validates** credentials against hashed password
- On success:
  - Issues JWT tokens (access + refresh)
  - Redirected to dashboard/home
- On failure:
  - Shows error message
  - Login form cleared for security

**4. Forgot Password**
- Enters email address
- **System sends reset link** via email (valid for 24 hours)
- User clicks link → Password reset form
- Enters new password twice
- **System validates:**
  - Password match
  - Password strength
  - Reset token validity
- Redirected to login with new password

---

### Phase 2: Profile & Preferences

**5. Profile Setup**
- After first login, user directed to complete profile
- Fills in personal information:
  - Full name
  - Phone number (with country code)
  - Date of birth
  - Address (Street, City, State, Postal Code)
  - Company/Organization (optional)
  - Profile picture (optional)

**6. Update Profile**
- Navigate to: Home → About → Profile section
- Edit any information:
  - Personal details
  - Contact information
  - Address
  - Preferences & notifications
- Save changes → Confirmation message

**7. View Favorites**
- Add halls to favorites while browsing
- Quick access to favorite halls
- Remove from favorites anytime

---

### Phase 3: Hall Browsing & Selection

**8. Navigate to Booking**
- Access navigation: Home, About, Category, Contact, Profile, **Start Booking**
- Or click "Start Booking" button on home page

**9. View Hall Categories**
- Browse 3 hall categories:
  - **Small** - 10-30 capacity (₹20-30/hour)
  - **Medium** - 31-60 capacity (₹40-60/hour)
  - **Large** - 61+ capacity (₹80-120/hour)
- Each category shows:
  - Hall name & description
  - Seating capacity
  - Amenities list
  - Average rating
  - Starting price

**10. Select & View Hall Details**
- Click on specific hall
- Details displayed:
  - 📷 Photo gallery
  - 🏛️ Description
  - 👥 Capacity (with layout diagram)
  - 🎛️ Equipment (projectors, microphones, WiFi, AC, etc.)
  - 💰 Pricing (per hour, with add-ons)
  - ⭐ Reviews & ratings
  - 📍 Location & directions
  - 🕐 Availability calendar

---

### Phase 4: Booking Selection & Scheduling

**11. Select Booking Date**
- Interactive calendar displayed
- Green dates = slots available
- Red dates = fully booked
- Click date to proceed
- **System applies Scheduling Algorithm** to calculate availability

**12. View Slot Availability**
- Time slots displayed: **8:00 AM to 8:00 PM** (hourly or half-hourly)
- **Color coding:**
  - 🟩 Green = Available slot
  - 🟥 Red = Booked/Unavailable
  - 🟨 Yellow = Partially available
- **Slot duration:** 1 hour, 2 hours, 4 hours, full day options
- Previous slots disabled (cannot book past times)

**13. Handle Unavailability**
- If no slots available:
  - Message: "Sorry, no availability for selected date"
  - Suggest alternative dates
  - Show similar halls with availability
- Customer can:
  - Select different date
  - Choose different hall
  - Go back to categories

**14. Select Start & End Time**
- Choose start time from available slots
- **System automatically calculates:**
  - Duration (hours)
  - Base cost (rate × hours)
  - Checkout time
- Choose end time
- Display total cost breakdown

---

### Phase 5: Booking Form & Add-ons

**15. Fill Booking Details Form**
- **Primary Information:**
  - Name (auto-filled from profile, editable)
  - Email (auto-filled from profile, editable)
  - Phone number (pre-filled, editable)
  - Address (pre-filled, editable)
  
**16. Booking Purpose & Additional Details**
- **Purpose of booking:**
  - Corporate meeting
  - Birthday party
  - Wedding function
  - Seminar/Conference
  - Other (text input)
- **Attendees count** (for catering estimation)
- **Special requests** (text area)

**17. Select Beverages & Add-ons**
- **Beverages:** Yes/No toggle
- **If Yes, select beverage type:**
  - Tea & Coffee
  - Soft Drinks
  - Water & Juice
  - Alcohol (if applicable)
  - Mixed package
- **Pricing:** Each add-on shows cost
  - Per person pricing
  - Quantity selector
  - Cost calculated automatically

**18. Select Menu Based on Beverage Type**
- **Tea & Coffee menu:**
  - Premium tea ₹50
  - Coffee ₹70
  - Hot chocolate ₹60
  - Add snacks (+₹100-300)
  
- **Soft Drinks menu:**
  - Coke/Pepsi ₹30
  - Juice varieties ₹40
  - Add snacks (+₹100-300)
  
- **Water & Juice:**
  - Bottled water ₹20
  - Fresh juice ₹100
  
- **Alcohol (if permitted):**
  - Beer varieties
  - Wine selections
  - Spirits
  
- **Mixed packages:** Pre-designed combinations

**19. Add Special Services (Optional Add-ons)**
- 🎤 Sound system rental (+₹500)
- 📽️ Projector & screen (+₹800)
- 🍽️ Catering service (+varies)
- 🪑 Extra chairs (+₹50/chair)
- 🪴 Decoration service (+₹2000-5000)
- 🎂 Cake & dessert (+varies)
- 🅿️ Parking arrangement (+₹100/vehicle)

**20. Display Total Cost Breakdown**
- Base hall cost: ₹5,000 × 4 hours = ₹20,000
- Beverages: ₹100 × 30 people = ₹3,000
- Add-ons: ₹1,300
- **Sub-total:** ₹24,300
- GST (18%): ₹4,374
- **Total Amount:** ₹28,674

---

### Phase 6: Terms, Conditions & Agreement

**21. Terms & Conditions**
- Expandable T&C section showing:
  - Cancellation policy (by time window)
  - Refund terms
  - Damage policy
  - House rules
  - Payment terms
  - User responsibilities
- **Checkbox:** "I agree to terms & conditions"
- Cannot proceed without checking

**22. Review Booking Summary**
- Display full booking summary:
  - Selected hall & date/time
  - Attendees & purpose
  - Selected beverages & menu
  - Add-ons selected
  - Total cost with tax breakdown
- Option to edit booking details
- Proceed to payment or cancel

---

### Phase 7: Payment Processing

**23. Payment Page**
- Display total amount to pay
- Payment method: **Razorpay integration**
- Razorpay widget loads
- Options available:
  - Credit/Debit card
  - NetBanking
  - UPI (Google Pay, PhonePe, Paytm)
  - Wallet
  - EMI options

**24. Payment Processing**
- User enters payment details
- **Razorpay processes** securely
- Shows loading state
- On success → Confirmation page
- On failure → Error message with retry option

**25. Payment Confirmation**
- ✅ Payment successful message
- Booking ID generated (e.g., #BK-2025-11-15-00042)
- Confirmation details displayed
- Email sent to customer

---

### Phase 8: Post-Booking Documents

**26. Invoice Generation**
- **Invoice generated** containing:
  - Booking ID & date
  - Hall details & address
  - Booking date/time & duration
  - Base cost breakdown
  - Add-ons & menu items
  - Total amount & payment status
  - Customer details & signature line
- **Format:** PDF downloadable
- **Sent via email** automatically

**27. Contract Form Generation**
- **Contract/Agreement generated** containing:
  - Hall usage terms
  - Cancellation & refund policy
  - Damage liability clause
  - Payment terms
  - Customer responsibilities
  - Hall house rules
  - Terms for add-on services
  - Signature fields (Customer & Vendor)
- **Format:** PDF with digital signature option
- **Sent via email** after booking confirmation

**28. Email Notification**
- **Email contains:**
  - Booking confirmation message
  - Invoice (PDF attached)
  - Contract/Agreement (PDF attached)
  - Hall location & directions
  - Vendor contact information
  - How to reschedule/cancel
  - Payment receipt
- **Sent to:** Customer email address

---

### Phase 9: Booking History & Management

**29. View Booking History**
- Navigate to: Profile → Booking History
- Display all bookings:
  - **Upcoming:** Blue badge
  - **Completed:** Gray badge
  - **Cancelled:** Red badge
  
- Each booking card shows:
  - Hall name & date/time
  - Booking status
  - Amount paid
  - Quick actions (View details, Cancel, Reschedule)

**30. Cancel Booking**
- Click "Cancel" on booking card
- Modal shows cancellation policy:
  - **48+ hours before:** 75% refund (25% fee)
  - **2-7 days before:** 50% refund (50% fee)
  - **7+ days before:** 75% refund (25% fee)
  - **< 2 hours before:** No refund
  
- Reason dropdown:
  - Plans changed
  - Event postponed
  - Better venue found
  - Budget issues
  - Other (text input)

- Confirm cancellation
- **System processes:**
  - Updates booking status to "Cancelled"
  - Calculates refund amount
  - Credits to wallet within 3-5 days
  - Sends cancellation email
  - Updates availability calendar

**31. Reschedule Booking**
- Click "Reschedule" on booking card
- Select new date from calendar
- View available time slots
- Can only change date/time, **NOT the hall**
- Recalculate cost if time duration changes
- Approve & confirm
- **System processes:**
  - Updates booking with new date/time
  - Sends new invoice & contract
  - Sends confirmation email
  - Updates calendar

**32. Cannot Change Hall or Category**
- Once booked, hall & category locked
- Customer cannot change to different hall
- Can only reschedule date/time
- To book different hall: Create new booking
- Old booking remains in history

---

### Phase 10: Wallet & Credits

**33. View Wallet**
- Navigate to: Profile → Wallet
- Display:
  - Current balance
  - Transaction history
  - Refund credits
  - Booking credits (if any)

**34. Manage Wallet**
- Add funds manually
- Use wallet balance for future bookings
- Receive refunds to wallet
- Download transaction history

---

## 🏢 MODERATOR/VENDOR USER FLOW

### Phase 1: Authentication & Dashboard

**1. Vendor Registration**
- Vendor fills registration form:
  - Business name
  - Email & password
  - Phone number
  - Business address
  - GST/Tax ID
  - Bank account details (for payouts)
- **System validates:**
  - Email uniqueness
  - Business details
  - Document verification (GST certificate, ID proof)
- Account created (pending approval)
- Approval email sent

**2. Vendor Login**
- Enter email & password
- **System validates** credentials
- Redirected to vendor dashboard
- Shows account approval status

**3. Dashboard Overview**
- **Dashboard displays:**
  - 📊 Total bookings (this month)
  - 💰 Total revenue (this month)
  - 👥 Total customers
  - 📅 Upcoming bookings (next 7 days)
  - 🔴 Pending approvals
  - ⭐ Average rating

---

### Phase 2: Venue & Room Management

**4. Manage Venues**
- Navigate: Dashboard → Venues
- Display all owned venues in card format:
  - Venue name, location
  - Status (Active/Inactive)
  - Number of rooms
  - Average rating
  - Actions: Edit, View, Delete

**5. Create New Venue**
- Click "Add Venue" button
- Fill venue form:
  - Venue name & description
  - Location (address, city, coordinates)
  - Contact phone & email
  - Website URL
  - Operating hours
  - Venue type (Hotel, Hall, Community Center, etc.)
  - Amenities checklist
  - Photo upload (gallery)
  - Parking details
  - Accessibility info

**6. Add Rooms/Halls to Venue**
- Click "Add Room" in venue
- Fill room form:
  - Room name
  - Seating capacity
  - Room type (Meeting room, Banquet, etc.)
  - Base price per hour
  - Available equipment:
    - ☑️ Projector
    - ☑️ WiFi
    - ☑️ Air conditioning
    - ☑️ Sound system
    - ☑️ Kitchen access
    - ☑️ Parking
  - Room photos/videos
  - Layout diagram upload
  - Description

**7. Manage Room Pricing**
- Set base hourly rate
- Define peak hours pricing (if applicable)
- Set minimum booking duration
- Define cancellation policy
- Set availability rules

**8. Update Room Status**
- Change room status:
  - 🟢 Active - Available for booking
  - 🟡 Maintenance - Unavailable temporarily
  - 🔴 Inactive - Not available
  - 🟣 Blocked - Manually blocked dates
- Reason for status change (optional)
- Effective date & time

**9. Manage Add-ons & Beverages**
- Create add-on services:
  - Service name & description
  - Price
  - Category (beverages, catering, equipment, decoration)
  - Availability (all rooms or specific rooms)
- Examples:
  - Tea & Coffee service
  - Soft drinks package
  - Sound system rental
  - Projector rental
  - Catering service

---

### Phase 3: Booking Management

**10. View All Bookings**
- Navigate: Dashboard → Bookings
- Display bookings in table/card format:
  - Customer name
  - Hall & date/time
  - Status (Pending, Confirmed, Completed, Cancelled)
  - Amount
  - Action buttons

**11. Filter & Search Bookings**
- Filter by:
  - ✓ Status (Pending, Confirmed, etc.)
  - ✓ Date range
  - ✓ Hall/Room
  - ✓ Amount range
- Search by:
  - ✓ Customer name
  - ✓ Booking ID
  - ✓ Phone number

**12. View Booking Details**
- Click booking to view complete details:
  - Customer information
  - Hall & exact time
  - Services & add-ons
  - Total amount & payment status
  - Special requests
  - Contract/Agreement
- Download invoice & contract
- View customer contact info

**13. Approve/Confirm Bookings**
- Click "Approve" on pending booking
- **System updates:**
  - Status changes to "Confirmed"
  - Confirmation email sent to customer
  - Calendar updated

**14. Handle Cancellation Requests**
- View cancellation requests from customers
- Review cancellation reason
- Calculate refund based on policy:
  - **48+ hours before:** 75% refund
  - **2-7 days before:** 50% refund
  - **7+ days before:** 75% refund
  - **< 2 hours before:** No refund
- Approve/Reject cancellation
- If approved:
  - Process refund
  - Send confirmation email
  - Update calendar

**15. Modify/Reschedule Bookings**
- If customer requests reschedule:
  - Check new date availability
  - Update booking details
  - Recalculate cost if needed
  - Send updated invoice & contract
  - Confirm with customer

---

### Phase 4: Revenue & Analytics

**16. View Revenue Reports**
- Navigate: Dashboard → Reports
- Display:
  - **Daily revenue** chart
  - **Monthly revenue** total
  - **Revenue by hall** breakdown
  - **Revenue by service** (beverages, add-ons, etc.)
  - **Average booking value**
- Filter by date range
- Export reports (PDF/Excel)

**17. View Booking Analytics**
- **Booking trends:**
  - Total bookings (trend graph)
  - Booking by hour
  - Booking by day of week
  - Popular time slots
- **Room utilization:**
  - Room occupancy rate %
  - Most booked room
  - Underutilized rooms
- **Customer insights:**
  - Repeat customers
  - New vs returning
  - Customer satisfaction ratings

**18. Generate Custom Reports**
- Create custom reports:
  - By date range
  - By room/hall
  - By service type
  - By customer
- Export formats: PDF, Excel, CSV
- Email reports to manager/accountant

---

### Phase 5: Profile & Settings

**19. Update Vendor Profile**
- Navigate: Settings → Profile
- Edit:
  - Business name & description
  - Contact information
  - Logo upload
  - Business hours
  - Cancellation policy
  - Refund policy
  - Terms & conditions

**20. Bank Account Settings**
- Add/Update bank account for payouts:
  - Account holder name
  - Account number
  - IFSC code
  - Bank name
- Payout schedule:
  - Weekly
  - Monthly
  - On-demand
- View payout history

**21. Notification Settings**
- Configure notifications:
  - Email for new bookings
  - SMS for cancellations
  - Daily summary email
  - Weekly analytics
  - Custom alerts

---

## 🔑 ADMIN USER FLOW

### Phase 1: Authentication & Dashboard

**1. Admin Login**
- Enter email & password
- **System validates** admin credentials
- Redirected to admin dashboard
- Welcome message with quick stats

**2. Admin Dashboard**
- **Key metrics displayed:**
  - 📊 Total bookings (all-time/this month)
  - 💰 Total revenue
  - 👥 Total customers
  - 🏢 Total venues/vendors
  - 🎯 Occupancy rate %
  - ⭐ System health status
  - 🚨 Pending approvals

---

### Phase 2: Booking Management

**3. View All Bookings**
- Navigate: Admin → Bookings
- Display all bookings (system-wide) in table format:
  - Booking ID, customer, hall
  - Date/time, amount
  - Status (Pending, Confirmed, Completed, Cancelled)
  - Vendor/venue name

**4. Filter & Search Bookings**
- Advanced filters:
  - ✓ Status (all options)
  - ✓ Date range
  - ✓ Amount range
  - ✓ Venue/Hall
  - ✓ Vendor
  - ✓ Customer segment
- Search by:
  - ✓ Booking ID
  - ✓ Customer name/email
  - ✓ Phone number
  - ✓ Venue name

**5. View Booking Card Format**
- Each booking shows:
  - 👤 Customer name & phone
  - 🏛️ Hall name & venue
  - 📅 Booking date & time
  - ⏱️ Duration
  - 💰 Total amount
  - 📊 Status badge
  - Quick action buttons

**6. Approve/Reject Bookings**
- Review pending bookings
- Click "Approve" → Booking confirmed, email sent
- Click "Reject" → Reason required, customer notified
- View approval history

**7. Cancel Bookings (Admin Authority)**
- Cancel any booking if needed:
  - Reason required (Venue unavailable, Policy violation, etc.)
  - Refund automatically calculated
  - Customer notified immediately
  - Refund processed within 24 hours

**8. Process Cancellation & Refund Requests**
- Navigate: Admin → Cancellations
- View pending cancellation requests:
  - Customer name & booking details
  - Reason for cancellation
  - Refund amount calculated
  - Time until refund deadline
- Actions available:
  - ✅ Approve refund (initiates payout)
  - ❌ Reject refund (with reason)
  - 💬 Send message to customer
- Generate refund report
- Track refund status

---

### Phase 3: Customer Communication

**9. View Contact Requests**
- Navigate: Admin → Contact & Queries
- Display all contact form submissions:
  - Name, email, phone
  - Subject
  - Message preview
  - Submission date
  - Status (New, Read, Replied)

**10. Reply to Queries**
- Click on query to view full message
- Rich text editor for reply:
  - Compose professional response
  - Add templates (for common questions)
  - Attach files (if needed)
  - Schedule send time (optional)
- Send reply (email sent automatically)
- Mark as "Replied"
- Archive old queries

**11. View Booking Enquiries**
- Navigate: Admin → Enquiries
- Display all customer booking enquiries:
  - Customer name & contact
  - Hall interest & requirements
  - Enquiry message
  - Date & priority level
- Reply to enquiries:
  - Send availability information
  - Send pricing details
  - Suggest alternative halls
  - Generate inquiry follow-up

**12. Customer Feedback & Reviews**
- View all customer reviews:
  - Hall ratings (1-5 stars)
  - Review text
  - Customer name
  - Date submitted
- Actions:
  - ✓ Publish/Hide review
  - ✓ Flag inappropriate reviews
  - ✓ Respond to reviews
  - ✓ Sort by rating/date

---

### Phase 4: Hall & Venue Management

**13. Manage All Venues**
- Navigate: Admin → Venues
- View all venues in system (all vendors):
  - Venue name, location
  - Vendor name
  - Rooms count
  - Status (Active/Inactive)
  - Rating & reviews count
  - Actions: View, Edit, Deactivate

**14. Add/Edit Hall Data**
- Create new hall/venue:
  - Admin can add directly
  - Or approve vendor submissions
- Edit existing hall:
  - Update pricing
  - Change capacity
  - Modify amenities
  - Upload new photos
  - Update description

**15. Manage Hall Status**
- Change status of any hall:
  - 🟢 Active - Available
  - 🟡 Maintenance - Unavailable temporarily
  - 🔴 Inactive - Disabled
  - 🟠 Under Review - Pending approval
- Reason for status change
- Effective immediately or scheduled
- Notification sent to vendor/customer

**16. Remove Halls**
- Deactivate/delete halls if needed:
  - Archive option (keeps data)
  - Delete option (permanent)
  - Reason required
  - Affected bookings handled
  - Vendor notified

---

### Phase 5: Vendor Management

**17. Approve New Vendors**
- Navigate: Admin → Vendors
- View pending vendor approvals:
  - Business name & owner
  - Submitted documents
  - Verification status
  - Submission date

**18. Verify Vendor Documents**
- Check submitted documents:
  - GST certificate
  - Business registration
  - ID proof
  - Address proof
  - Bank account details
- Actions:
  - ✅ Approve vendor
  - ❌ Reject (with reason for resubmission)
  - ⏳ Request more documents

**19. Manage Vendor Status**
- View all vendors with status:
  - Active, Inactive, Suspended, Banned
  - Change status if needed
  - Reason for status change
- Suspend vendor if violations detected
- Ban vendor for policy breaches

**20. Monitor Vendor Performance**
- View vendor analytics:
  - Total bookings
  - Revenue generated
  - Customer ratings
  - Cancellation rate
  - Response time
  - Complaint rate
- Identify underperforming vendors
- Recognition for top vendors

---

### Phase 6: System Notifications

**21. Send Notifications**
- Navigate: Admin → Notifications
- Send system-wide notifications:
  - **Booking Confirmations:**
    - Auto-send on booking confirmation
    - Customizable template
    - Include booking details
  - **Booking Reminders:**
    - 24 hours before booking
    - 1 hour before booking
    - Day after completion (feedback request)
  - **Cancellation Notices:**
    - Auto-send on booking cancellation
    - Include refund details
  - **System Alerts:**
    - Backup notifications
    - Maintenance alerts
    - Important announcements
  - **Custom Notifications:**
    - Create custom messages
    - Target specific users/vendors
    - Schedule send time
    - Track delivery & open rates

**22. Notification History**
- View all sent notifications:
  - Date, time, type
  - Recipient count
  - Delivery status
  - Open rate
  - Response rate (if applicable)
- Resend notifications if needed

---

### Phase 7: Reports & Analytics

**23. Generate Booking Reports**
- Navigate: Admin → Reports → Bookings
- Report options:
  - **By User:** All bookings by customer, with analysis
  - **By Hall:** Occupancy & revenue by hall
  - **By Date:** Bookings for specific date range
  - **By Status:** Count by status (pending, confirmed, etc.)
  - **By Vendor:** Performance report by vendor
  - **Revenue Report:** Total revenue breakdown

**24. Report Features**
- Interactive charts:
  - 📊 Bar charts (revenue trends)
  - 📈 Line graphs (booking trends)
  - 🥧 Pie charts (category breakdown)
- Filters:
  - Date range (custom or preset)
  - Venues/halls
  - Vendors
  - Booking status
- Export options:
  - 📄 PDF format
  - 📑 Excel format
  - 📋 CSV format
- Email report to stakeholders
- Schedule recurring reports

**25. User Analytics**
- **Customer insights:**
  - Total users registered
  - New users (this month/week)
  - Active users (booked in last 30 days)
  - User segmentation (by activity, location, etc.)
  - Retention rate %
  - Customer lifetime value
  - Churn analysis

**26. Revenue Analytics**
- **Financial overview:**
  - Total revenue (all-time/this month)
  - Revenue by venue/hall
  - Revenue by service (beverages, add-ons, etc.)
  - Average booking value
  - Revenue growth trend
  - Vendor commission breakdown
  - Refund analysis (amount, count, %age)

**27. System Health Reports**
- Monitor system performance:
  - API response times
  - Database health
  - Server uptime
  - User concurrent sessions
  - Error rates & logs
  - Storage usage

---

### Phase 8: Backup & Recovery

**28. Initiate System Backup**
- Navigate: Admin → Backup & Recovery
- Click "Start Backup"
- **System backs up:**
  - 📋 Users & profiles
  - 📅 Bookings & history
  - 💬 Contact requests
  - 🍽️ Food/beverage orders
  - 📊 Reports & analytics data
  - 🏢 Venue & room data
  - 📧 Email logs
  - 🖼️ All uploaded media
  - CMS content

**29. Check Storage Before Backup**
- System automatically checks:
  - Available storage space
  - Backup size (estimated)
  - Required space
- If insufficient storage:
  - Alert shown
  - Recommend cleanup
  - Show option to purchase storage
  - Block backup until resolved

**30. Display Disclaimer Alert**
- Before restoring data, show disclaimer:
  ```
  ⚠️ WARNING: Data Restore
  - This will OVERWRITE current data
  - All changes since backup will be LOST
  - Process cannot be undone
  - Recommend taking backup before restore
  - Continue? [YES / NO]
  ```
- Require admin confirmation

**31. Configure Automatic Backups**
- Schedule backups:
  - 📅 Daily (time: 02:00 AM default)
  - 📅 Weekly (day: Sunday, time: 02:00 AM)
  - 📅 Monthly (date: 1st of month, time: 02:00 AM)
- Multiple schedules possible
- Enable/disable toggle
- Edit schedule anytime
- Send confirmation email after backup

**32. View Backup Logs**
- Navigate: Admin → Backup Logs
- Display all backup operations:
  - **Backup logs show:**
    - Date & time of backup
    - Admin who initiated
    - Backup size
    - Backup type (full/incremental/manual)
    - Status (Success/Failed)
    - Duration taken
    - Data integrity check result
    - Restore logs show:**
    - Date & time of restore
    - Admin who initiated
    - Data restored count
    - Duration taken
    - Pre-restore backup taken? (Yes/No)
    - Status (Success/Failed)
    - Rollback timestamp (if needed)

**33. Download Backup Files**
- View all available backups:
  - List of backup files
  - Size of each
  - Creation date/time
  - Last accessed
- Download options:
  - ✓ Download individual backup
  - ✓ Download multiple backups
  - ✓ Auto-archive to cloud (optional)
- Backup verification:
  - Check integrity before download
  - Generate checksum/hash
  - Verify no corruption

**34. Store Offline**
- Downloaded backups can be:
  - Stored on external hard drive
  - Transferred to cloud storage (Google Drive, OneDrive, S3)
  - Burned to DVD/Blu-ray
- Recommend 2 offline copies at different locations
- Maintain backup log with storage location

**35. Restore Data**
- Navigate: Admin → Restore
- Select backup to restore from:
  - List of available backups
  - Preview restore date/time/size
- Choose restore type:
  - **Full Restore:** All data from backup
  - **Selective Restore:** Choose specific modules:
    - ☑️ Only bookings
    - ☑️ Only users
    - ☑️ Only content
    - ☑️ Only reports
    - ☑️ Combination of selected
- Confirm:
  - Show disclaimer
  - Backup current data first (auto)
  - Proceed with restore

**36. Handle Restore Completion**
- **Verify data integrity:**
  - Check for duplication
  - Verify record counts
  - Validate data consistency
  - Run integrity checks
- **Potential issues handled:**
  - Duplicate bookings → Merge
  - Orphaned records → Clean
  - Missing references → Flag for review
  - Data conflicts → Use timestamp to resolve
- Generate restore report
- Send confirmation email
- Log all actions

**37. Rollback if Needed**
- If restore causes issues:
  - Option to rollback to pre-restore state
  - Automatic backup taken before restore
  - One-click rollback
  - Restore previous state
  - Notify admin
  - Log rollback action

---

### Phase 9: System Settings & Configuration

**38. Manage System Settings**
- Navigate: Admin → Settings
- Configure:
  - 🏢 Platform name & branding
  - 💰 Currency & timezone
  - 📧 Email configuration (SMTP)
  - 📱 SMS gateway (for notifications)
  - 🎨 Theme & UI customization
  - 🔐 Security policies (password requirements, etc.)

**39. CMS Management**
- Manage website content:
  - Homepage content
  - About page
  - Terms & conditions
  - Privacy policy
  - FAQs
  - Blog posts
  - Static pages
- Rich text editor with preview
- Publish/Draft/Schedule posts
- Media library management

**40. User Role Management**
- Create/Edit user roles:
  - Admin
  - Moderator/Vendor
  - Customer
  - Guest
  - Custom roles (if needed)
- Assign permissions per role
- View role statistics

---

## 📊 Cross-Cutting Concerns

### Availability Processing
- **All roles:** System applies scheduling algorithms
  - Checks existing bookings
  - Calculates free slots
  - Prevents double-booking
  - Handles overlapping times
  - Applies venue-specific rules

### Payment Processing (Razorpay)
- Triggered at checkout
- Secure payment gateway integration
- Multiple payment methods
- Transaction logging
- Automated reconciliation

### Email Notifications
- Triggered automatically on:
  - Booking confirmation
  - Booking cancellation
  - Booking reschedule
  - Payment receipt
  - Password reset
  - New vendor approval
  - Query replies
- Templates customizable by admin
- Tracking of delivery & opens

### Document Generation
- Invoice generation (automated)
- Contract generation (automated)
- Report generation (on-demand)
- PDF format with digital signatures
- Email attachment

---

## 🎯 Summary of Role Workflows

| Feature | Guest | Customer | Vendor | Admin |
|---------|:-----:|:--------:|:------:|:-----:|
| Browse Halls | ✅ | ✅ | ✅ | ✅ |
| Create Booking | ❌ | ✅ | ✅ | ✅ |
| Manage Bookings (own) | ❌ | ✅ | ✅ | - |
| Manage Bookings (all) | ❌ | ❌ | ❌ | ✅ |
| Create Venues | ❌ | ❌ | ✅ | ✅ |
| Approve Vendors | ❌ | ❌ | ❌ | ✅ |
| View Analytics | ❌ | Limited | ✅ | ✅ |
| Manage Backups | ❌ | ❌ | ❌ | ✅ |
| System Config | ❌ | ❌ | ❌ | ✅ |

---

**Document Version:** 2.0  
**Last Updated:** November 15, 2025  
**Status:** Current & Complete ✅
