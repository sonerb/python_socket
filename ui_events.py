from PyQt5.QtGui import QStandardItemModel, QStandardItem

class UI_Events(object):
    def __init__(self, app, ui, client):
        self.ui = ui
        self.app = app
        self.client = client

    def btn_connect_clicked(self):
        username = self.ui.txt_username.text()
        self.client.connect()
        self.client.start()
        self.client.set_username(username)
    
    def btn_disconnect_clicked(self):
        self.client.disconnect()

    def btn_send_clicked(self):
        message = self.ui.txt_message.text()
        self.client.talk(message)
        self.ui.txt_message.setText('')

    def txt_message_enter(self):
        self.btn_send_clicked()

    def on_message(self, msg):
        self.ui.txt_chat.append(msg)

    def on_user_list(self, obj):
        # Create an empty model for the list's data
        model = QStandardItemModel(self.ui.lst_users)

        for user in obj:
            # create an item with a caption
            item = QStandardItem(user)        
            # Add the item to the model
            model.appendRow(item)
        
        # Apply the model to the list view
        self.ui.lst_users.setModel(model)
    
    def on_connect(self):
        self.ui.btn_connect.setVisible(False)
        self.ui.actionConnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(True)
        self.ui.btn_disconnect.setVisible(True)
        self.ui.statusbar.showMessage('Connected')
        self.ui.txt_message.setReadOnly(False)
        self.ui.txt_username.setReadOnly(True)

    def on_disconnect(self):
        self.ui.btn_disconnect.setVisible(False)
        self.ui.actionDisconnect.setVisible(False)
        self.ui.actionConnect.setVisible(True)
        self.ui.btn_connect.setVisible(True)
        self.ui.statusbar.showMessage('Disconnected')
        self.ui.txt_message.setReadOnly(True)
        self.ui.txt_username.setReadOnly(False)

    def on_close(self):
        self.app.closeAllWindows()

    def closeEvent(self, QCloseEvent):
        self.client.stop()