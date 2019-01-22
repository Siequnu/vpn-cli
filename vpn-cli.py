import urwid
import paramiko
import os
import glob
import subprocess

def get_main_servers ():
	servers = []
	for file in glob.glob("/home/pi/ovpn_servers/*.ovpn"):
		servers.append(os.path.basename(file))
	return servers

def update_text(read_data):
	global text
	text.set_text(str(text.text) + str(read_data.decode()))

def enter_idle():
	loop.remove_watch_file(pipe.stdout)

def menu(title, choices):
	body = [urwid.Text(title), urwid.Divider()]
	for c in choices:
		button = urwid.Button(c)
		urwid.connect_signal(button, 'click', item_chosen, c)
		body.append(urwid.AttrMap(button, None, focus_map='reversed'))
	return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_chosen(button, choice):
	
	global text	
	text = urwid.Text('Connecting to: ' + str(choice) + '\n')
	widget = urwid.Filler(text, 'top')

	top = urwid.Overlay(widget, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
		align='center', width=('relative', 85),
		valign='middle', height=('relative', 80),
		min_width=20, min_height=9)
	
	loop = urwid.MainLoop(top, unhandled_input=exit_program, palette=[('reversed', 'standout', '')])
	
	stdout = loop.watch_pipe(update_text)
	stderr = loop.watch_pipe(update_text)
	arguments = ['sudo /usr/local/sbin/openvpn --config /home/pi/ovpn_servers/' + choice+ ' --auth-user-pass /etc/openvpn/auth.txt']    
	p = subprocess.Popen(arguments, stdout=stdout, stderr=stderr, universal_newlines=True, shell=True)
	loop.run()

def exit_program(button):
	if button in ['q', 'm']:
		killall_openvpn()
		main_menu()
	if button in ['m']:
		killall_openvpn()
		main_menu()

def killall_openvpn():
	subprocess.Popen(['sudo', 'killall', 'openvpn'])
	
def main_menu ():
	killall_openvpn()
	choices = get_main_servers()
	main = urwid.Padding(menu(u'VPN Servers', choices), left=2, right=2)
	top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
		align='center', width=('relative', 60),
		valign='middle', height=('relative', 60),
		min_width=20, min_height=9)
	urwid.MainLoop(top, unhandled_input=exit_program, palette=[('reversed', 'standout', '')]).run()
	
main_menu()