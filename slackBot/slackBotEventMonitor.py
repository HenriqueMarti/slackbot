# coding=utf-8

from threading import Thread
import time


class SlackBotEventMonitor(Thread):
    # "Constantes" que definem os eventos a tratas
    HELLO_EVENT = 'hello'
    PRESENCE_CHANGE_EVENT = 'presence_change'
    RECONNECT_URL_EVENT = 'reconnect_url'
    USER_TYPING_EVENT = 'user_typing'
    MESSAGE_EVENT = 'message'

    def __init__(self, slackbot):
        Thread.__init__(self)

        self.active = False
        self.paused = False
        self.connected = False

        # obtem os objetos de controle
        self.__bot = slackbot
        self.__slackClient = slackbot.slackClient

    def start(self):
        if not self.active:
            # Se é o "1º Start" eu dou um Start Real na Thread (estou chamando o método start() da superclasse, ou seja, o start() ancestral)
            super(SlackBotEventMonitor, self).start()
        else:
            # Se a Thread já estiver iniciada eu só dou o "Resume"
            self.paused = False

    def stop(self):
        if self.active:
            self.paused = True

    def destroy(self):
        if self.active:
            self.active = False

    def run(self):
        self.active = True
        while self.active:
            # Se nao estiver com RTM conectado tenta conexao
            if not self.connected:
                self.connected = self.__slackClient.rtm_connect()
                if not self.connected:
                    print 'Connection Failed'

            # Se a conexao RTM estiver ativa faz o tratamento dos eventos recebidos
            if self.connected:
                events = self.__slackClient.rtm_read()

                # Se estiver em pause eu recebo o evento e ignoro. Eu estava realmente dando pause na thread,
                # mas os eventos iam ficando em buffer e na volta todos eram disparados.
                if self.paused:
                    continue

                if len(events) > 0:
                    for event in events:
                        if 'type' in event.keys():
                            event_type = str(event['type'])

                            # Chama o tratamento para o event "hello"
                            if (event_type == SlackBotEventMonitor.HELLO_EVENT) and bool(self.__bot.OnHelloEvent.receivers):
                                self.__bot.OnHelloEvent.send()

                            # Chama o tratamento para o event "presence_change"
                            if (event_type == SlackBotEventMonitor.PRESENCE_CHANGE_EVENT) and bool(self.__bot.OnPresenceChangeEvent.receivers):
                                self.__bot.OnPresenceChangeEvent.send()

                            # Chama o tratamento para o event "reconnect_url"
                            if (event_type == SlackBotEventMonitor.RECONNECT_URL_EVENT) and bool(self.__bot.OnReconnectUrlEvent.receivers):
                                self.__bot.OnReconnectUrlEvent.send()

                            # Chama o tratamento para o event "user_typing"
                            if (event_type == SlackBotEventMonitor.USER_TYPING_EVENT) and bool(self.__bot.OnUserTypingEvent.receivers):
                                self.__bot.OnUserTypingEvent.send(data=event)

                            # Chama o tratamento para o event "message"
                            if (event_type == SlackBotEventMonitor.MESSAGE_EVENT) and bool(self.__bot.OnMessageEvent.receivers):
                                self.__bot.OnMessageEvent.send(data=event)

                time.sleep(0.5)
