// CONFIG IN JS
const CONFIG_FILE_NAME	   = "config.json";
const print                = console.log;

// INSTANCES
const SAVE_SETTINGS_BUTTON = document.getElementById('save_settings');
const SEND_MESSAGE_TO      = document.getElementById('send_message_to');
const SEND_TO_ALL_USERS    = document.getElementById('send_all_check');
const SEND_MESSAGE_BUTTON  = document.getElementById('send_message_button');
const RUN_BUTTON           = document.getElementById('run_button');
const STOP_BUTTON          = document.getElementById('stop_button');
const UPDATE_BUTTON        = document.getElementById('update_button');

// VARS
window.settings = {
	"token"                  : document.getElementById('token')                 ,
	"default_message"        : document.getElementById('default_message')       ,
	"db_name"                : document.getElementById('db_name')               ,
	"message_repl"           : document.getElementById('message_repl')          ,
	"start_message"          : document.getElementById('start_message')         ,
	"upd_time"               : document.getElementById('upd_time')              ,
	"categories"             : document.getElementById('categories')            ,
	"category_nufic_message" : document.getElementById('category_nufic_message'),
	"no_film_error"          : document.getElementById('no_film_error')         ,
	"global_unsubscribe"     : document.getElementById('global_unsubscribe')    ,
	"unsibscribe_category"   : document.getElementById('unsibscribe_category')  ,
	"category_not_found"     : document.getElementById('category_not_found')    ,
	"subscribe_category"     : document.getElementById('subscribe_category')    ,
	"categories_text"        : document.getElementById('categories_text')       ,
	"base_message"           : document.getElementById('base_message')
};


function set_settings(settings) {
	for (var [key, value] of Object.entries(settings)) {
		if (key in window.settings){
			if ( typeof(value) == "object") {
				value = JSON.stringify(value).replaceAll(",", ",\n").replace("{", "{\n").replace("}", "\n}")
			}
			window.settings[key].value = value;
		}
	}
}


async function set_available_users(){
	document.querySelector("option[default]").remove();
	var chats = await eel.get_chats()();
	console.log(chats)
	chats.forEach(chat => {
		var chat_info = [chat[1], `${chat[0]} : ${chat[3]} ${chat[4]}`];
		var elem = document.createElement('option');

		elem.value = chat_info[0];
		elem.innerHTML = chat_info[1];

		SEND_MESSAGE_TO.appendChild(elem);
	})
}


async function send_message() {
	var message = document.getElementById('messge_to_users').value;
	if (message.length < 1){
		return
	}

	if (SEND_TO_ALL_USERS.checked) {
		await eel.send_message(message, true)();
	}
	else{
		await eel.send_message(message, false, SEND_MESSAGE_TO.value)();
	}
}


window.onload = async e => {
	let settings = await eel.read(CONFIG_FILE_NAME)();
	await set_settings(JSON.parse(settings));
	await set_available_users();

	RUN_BUTTON.addEventListener('click', async ()=>{
		await eel.re_init();
		var started = await eel.start(true)();
		if (started) {
			print('SUCCESS - Started');
		}
		else{
			print('Error - bot not started [for debug run with terminal]');	
		}
	});

	UPDATE_BUTTON.addEventListener('click', async ()=>{
		await eel.re_init();
		var started = await eel.update()();
		if (started) {
			print('SUCCESS - Started');
		}
		else{
			print('Error - bot not started [for debug run with terminal]');	
		}
	});

	STOP_BUTTON.addEventListener('click', async ()=>{
		await eel.re_init();
		var stoped = await eel.stop()();
		if (stoped) {
			print('SUCCESS - Stoped');
		}
		else{
			print('Error - bot not Stoped [for debug run with terminal]');	
		}
	});

	SEND_MESSAGE_BUTTON.addEventListener("click", async ()=>{
		await eel.re_init();
		await eel.start(false)();
		await send_message();
		await eel.stop()();
	});

	SAVE_SETTINGS_BUTTON.addEventListener("click", async ()=>{
		await eel.re_init();
		for (var [key, value] of Object.entries(window.settings))
		{
			window.settings[key] = window.settings[key].value;
		}
		console.log(window.settings)
		await eel.write(CONFIG_FILE_NAME, JSON.stringify(window.settings));
	});
}
