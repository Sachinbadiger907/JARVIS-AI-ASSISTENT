"""
Jarvis WhatsApp Sender - sends WhatsApp messages by voice command
"""

import pywhatkit


# Auto-generated from your exported contacts, plus manually added ones
CONTACTS = {
    "ddh vadokan": "+911800212212",
    "shivaji": "+919141345078",
    "paravva atti": "+919148512745",
    "indane gas book": "+918454955555",
    "amma": "+918150891895",
    "bhuvan": "+918105114357",
    "basavaraj k hugar": "+919880137619",
    "amogh": "+919686787576",
    "burhan clg": "+919019298896",
    "shivu": "+919535341385",
    "scl kannada mam": "+917760091678",
    "siddharth r k": "+919686239537",
    "dipali clinic": "+918296275043",
    "tanuja hugar": "+919900607619",
    "charan clg": "+919364888456",
    "yallappa unkal": "+919880006815",
    "appa": "+919902222128",
    "sagar clg": "+919886056695",
    "abhishek clg": "+918660361605",
    "arvind clg": "+916360465509",
    "madhu anty hubli": "+919611516564",
    "abhi clg": "+918762450158",
    "guru kiran badiger": "+918152011416",
    "zerox": "+917676920522",
    "rahul clg": "+919886325777",
    "komal clg": "+808088203337",
    "channamma anty hbl": "+917204828033",
    "pg": "+917795089853",
    "rohit clg": "+919141214306",
    "harish mava sld": "+919538373826",
    "goudar sir": "+919480325005",
    "malik clg": "+919972357596",
    "sharat clg": "+918147884184",
    "denial sir": "+919845309891",
    "sharada aunty": "+917483785006",
    "sambo badiger": "+919972939003",
    "basavaraj s kammar": "+919108445665",
    "shankrana kolur badgi": "+919535677265",
    "prakashgoud ganagir kittali": "+919743228706",
    "gurunathswami mahapurush": "+919845122381",
    "shivanand shirur": "+919972843335",
    "basavaraj s gaddi": "+919964799297",
    "devevdra pattar": "+918105748488",
    "manju sir tution": "+919986230505",
    "prakash moody": "+917090096059",
    "ashok": "+919980794105",
    "nagalingppa badager": "+919964045012",
    "basayya hosamani": "+919844033241",
    "shama": "+917338476897",
    "sevapp shirol hurali": "+917829171020",
    "pakirappa s sungar": "+919945230376",
    "neelappa ajja mailara": "+916363536547",
    "basappa basu": "+917204720985",
    "basangouda mulakipatil": "+918217885669",
    "nadaf badiger nadaf": "+918861523825",
    "daranesh jr": "+919945006107",
    "veeranagouda kalli": "+917353108470",
    "sharanappa kadapannavar": "+919686761181",
    "riyaz auto": "+919880850514",
    "aaban m": "+917795017795",
    "veeresh i b": "+918296419070",
    "gangadhar bhojashettar": "+919448551389",
    "venkanna kongwad": "+919731918588",
    "rudrappa badiger": "+918792052483",
    "bhimanna cheleri": "+918618449368",
    "manju badiger": "+918217835353",
    "chinnac": "+919591579076",
    "srisail kaka": "+919380125380",
    "veerabhadrayya javali krtc": "+918971687799",
    "shrishail badiger": "+919380125380",
    "kumar mava sld": "+919380000313",
    "basanagouda guranagoudra": "+917760958105",
    "yachcharappa badiger": "+919449971416",
    "n s shirol s": "+918904867226",
    "b s f kittali": "+917090613772",
    "h s madivalar madivalara": "+917795425357",
    "sachin badiger": "+916360972761",
    "h s gaddigoudra": "+918970498610",
    "paravva chikknaragund": "+919535028605",
    "ashok shirakol": "+917676665726",
    "siddu betasur": "+919380547984",
    "channamma hogar shirol": "+917899309336",
    "ganesh pawar": "+919742867819",
    "dth naggish marigoudara": "+919663879963",
    "jeevandhar kumar sdm": "+916362288335",
    "muttu muttu m": "+919743241305",
    "ramanna badeger": "+919902667795",
    "ghanesha": "+919742867819",
    "d2h technician": "+919663879963",
    "hulkoti clg": "+918073710365",
    "hulkoti engnieer clg": "+918310743079",
    "hulkoti engnieer college": "+917019944673",
    "makutappa talawar r naganur": "+917760733465",
    "mamadapur math manju": "+919845569129",
    "chinmay clg": "+918951348184",
    "9480614522": "+919480614522",
    "nagaraj kaka": "+918904867226",
    "infotech": "+917353661577",
    "infotech dharwad": "+918867283807",
    "data entry benglore 2": "+917411099890",
    "data entry benglore": "+919148884322",
    "sagar": "+918050787595",
    "clg english mam": "+919036432889",
    "clg clark": "+919964598725",
    "thontdyr clg": "+919481927413",
    "naragund": "+919980218346",
    "thontdyr": "+919448232035",
    "arun": "+918088663382",
    "keb shankar unkal": "+919886054081",
    "rajeshwari ant": "+919606449832",
    "clg chemistry mam": "+918105954579",
    "laptop": "+919844000017",
    "basappa bairappanavar": "+917483100189",
    "pg anty": "+919725858621",
    "prashant kaka": "+919449964301",
    "police anty": "+919036824339",
    "data": "+919900932606",
    "ningappa gujannavar": "+919620406135",
    "sachin clg": "+917019293973",
}


class WhatsAppSender:

    def send_message(self, contact_name: str, message: str) -> bool:

        contact_name = contact_name.strip().lower()

        phone_number = CONTACTS.get(contact_name)

        # Try a partial match if exact name wasn't found (e.g. "mom" matches "mom dear")
        if not phone_number:
            for name, number in CONTACTS.items():
                if contact_name in name or name in contact_name:
                    phone_number = number
                    break

        if not phone_number:
            print(f"No phone number saved for '{contact_name}'. Add it to CONTACTS in whatsapp_sender.py")
            return False

        try:
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=20,
                tab_close=False,
                close_time=5
            )
            return True

        except Exception as e:
            print(f"WhatsApp send error: {e}")
            return False