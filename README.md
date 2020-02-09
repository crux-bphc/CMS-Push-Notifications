# Fetch-Courses
This python script get user courses and stores their modules in an sqlite database. It can detect when new modules are uploaded, send push notifications to iOS devices, and will add them to the database.

# Installation
1. Clone this repository.

2. Install the necessary packages.

3. Get your device token from the Xcode console when you run the Push Notifications branch of the [CMS iOS](https://github.com/crux-bphc/CMS-iOS/tree/PushNotifications) app on your device.

4. Download the certificate file from the Apple Developer website: Certificates, Identifiers & Profiles -> Identifiers pane -> com.crux-bphc.CMS-iOS -> Push Notifications.
5. Open this certificate in Keychain Access.
6. In the Category pane on the left in Keychain access, navigate to certificates and then find the push notifications certificate.
7. Press the arrow to expand the certificate to show the private key.
8. Right click and export, one by one both the certificate and private key without any password.
9. Convert both files to .pem by running `openssl pkcs12 -in inputname.cer -out outputname.pem -nodes`
Change inputname to the file name and `.cer` to `.p12` for the key file.
10. Place both these `.pem` files in the current directory.
11. Execute `fetch.py`.
