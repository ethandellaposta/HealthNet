Welcome to Team Chain Reaction’s implementation of HealthNet! Before you begin to use our product, please take note of the following items:

Instructions for running the code:

Before attempting to run HealthNet, please ensure that Python version 3.4 or higher, Django version 1.9.1 is installed on the machine.

If using product from SVN repo and the database appears to not be working, run the following commands:
python3 manage.py makemigrations HealthNet
python3 manage.py migrate

If the superuser account for the Django admin site does not appear to be working, then run the following command:
python3 manage.py createsuperuser

If any of the below accounts are not working, then create the desired accounts through the Django
admin.

In order to run the code, either:
1. Press the green run triangle in the PyCharm IDE, or
2. Open up the command line
3. cd into the directory containing the manage.py file for this project. It should require one use of the command “cd HealthSite”
4. Run the command “python3 manage.py runserver”
5. Copy and paste the provided link into a web browser

To end the session, either hit the red stop square in the IDE, or hit Ctrl + C in the command line

In order to log in as a patient, please use the following credentials:
Username: alb6060
Password: sister

Username: BenSacco
Password: boyfriend

In order to log in as a system administrator, please use the following credentials:
Username: theodorabendlin
Password: Hogwarts!

In order to log in as a Hospital Administrator, please use the following credentials:
Username: trb7281
Password: admin

Username: JazzSale
Password: admin

In order to log in as a Hospital Doctor, please use the following credentials:
Username: EDellPost
Password: doctor

Username: BugBunny
Password: doctor

Username: JoeDough
Password: doctor

In order to log in as a Hospital Nurse, please use the following credentials:
Username: CBendlin
Password: nurse

While using this first version of HealthNet, please enjoy the following implemented features:
- Creation of patient account
- Creation of a Hospital Admin from the django administrator, or from the account
    of another Hospital administrator
- Modification of patient profile information from a patient account
- Viewing of Patient Profile information from a doctor or nurse account
- Modificiation of patient medical information by a patient's doctor
- Export of patient information in a .csv file
- Creation or modification fo a patient appointment
- Cancellation of patient appointment
- An appointment calendar to hold all appointments
- The addition/ removal of prescriptions for a patient by a doctor
- Viewing of patient medical information, prescriptions and tests results
- The release of test results by doctors
- Logging of system activities
- Admission or discharge of a patient from a hospital
- The ability to view activity log or viewing system statistics
- The ability to transfer patients between hospitals
- The ability to upload patient information
        Doctors are unable to upload images at this time
- The ability to send private messages

While using HealthNet, please take note of the following bugs that will be fixed upon the next release:
- The patient is able to update his or her account with invalid or missing fields
- The doctor is unable to upload an image to accompany patient test results


Note:  public_html/Release-2-beta/cross-team-testing also contains our Test Plan Document, titled Test Plan Tracker.  It
 also contains our Requirements Document, titled Requirements-HealthNet.doc

If you have any questions, please contact:
    Test Liason:  Theodora Bendlin; trb7281@g.rit.edu
     
Thank you for using this version of HealthNet!

- Team Chain Reaction (201605-02-SWEN-261-Team-B-ChainReaction)
