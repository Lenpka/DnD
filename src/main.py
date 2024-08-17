"""Пример работы с чатом через gigachain"""
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat
from random import randint
names = {1:" Борис", 2:"Евгений", 3: "Леонид", 4:"Александр", 5:"Платон", 6:"Сергей", 7:"Юрий", 8:"Станислав", 9:"Артём", 10:"Виктор"}
protagonist_name = "Главный герой"
storyteller_name = "Мастер игры, рассказчик"
second_player_name = names[randint(1,10)]
quest = "Пройти через подземелье и победить всех монстров, попутно прокачивая своего персонажа."
word_limit = 75  # word limit for task brainstorming
role_game_master = 'game_master'
role_player = 'player'

player_descriptor_system_message = SystemMessage(
    content="Действие происходит во вселенной Dungeons and Dragons. Задача квеста - пройти через подземелье и победить всех монстров. Среди героев победит тот, у кого больше уровней. игре Dungeons & Dragons персонажи развиваются, получая опыт и повышая уровень. Каждый новый уровень даёт персонажу новые возможности и способности.Прокачка персонажа происходит следующим образом: когда персонаж получает достаточно опыта, он может повысить свой уровень. Количество необходимого опыта зависит от уровня персонажа. После повышения уровня персонаж может выбрать новые навыки, способности или улучшить уже имеющиеся."
)

game_description = f"""Мы будем играть в Dungeons & Dragons. Задание: {quest}.
        Главный игрок - {protagonist_name}.
        Второй игрок - {second_player_name}
        Ведущий - рассказчик, {storyteller_name}."""


class Bot:
    def __init__(self, credentials) -> None:

        self.chat = GigaChat(model="GigaChat-Pro",credentials=credentials)
        self.visual_chat = GigaChat(model="GigaChat-Pro",credentials=credentials)
        self.messages = []

    def _prepare(self, game_mode) -> None:
        storyteller_description = (
            'Ты — мастер игры в Dungeons & Dragons. Это значит, что ты создаешь мир, в котором будут происходить приключения персонажей. Ты задаешь вопросы, которые помогают тебе понять, как персонажи видят этот мир, и предлагаешь им ситуации, в которых они могут проявить себя.Ты можешь создать для игроков любое приключение, которое они захотят. Ты также можещб создать для игроко персонажа, если у него нет времени или желания делать это самостоятельно.'
        )
        
        if game_mode == role_game_master:
            self.messages.append(SystemMessage(
                content=(
                    f"""{game_description}
                    Никогда не забывай, что ты рассказчик - {storyteller_name}, а я главный герой - {protagonist_name}, а третий игрок - {second_player_name}. 
                    Вот описание твоего персонажа: {storyteller_description}.
                    Не говори о себе, говори и запоминай о мире игры.
                    Для описания движений собственного тела заключите описание в «*».
                    Не меняй роли!
                    Не говори с точки зрения персонажа {protagonist_name} или {second_player_name}.
                    Иногда создавай различные игровые события.
                    Запомни, что ты рассказчик - {storyteller_name}.
                    Прекращай говорить, когда тебе кажется, что ты закончил мысль.
                    Отвечай коротко, одной строкой, уложись в {word_limit} слов или меньше.
                    Не отвечай одно и то же! Развивай историю, совершай новые активные действия. Меньше говори и больше действуй, чтобы сюжет развивался. Читателю должно быть интересно.
                    """
                )
            ))
        else:
            self.messages.append(SystemMessage(
                content=player_descriptor_system_message.content,
            ))

    def _start(self, game_mode) -> str:
        if game_mode == "game_master":
            quest_specifier_prompt = [
                HumanMessage(
                    content=f"""{game_description}
                    
                    Ты - рассказчик, {storyteller_name}.
                    Пожалуйста, напиши вводную фразу для начала истории. Будь изобретателен и креативен.
                    Пожалуйста, уложись в {word_limit} слов или меньше.
                    Обращайся непосредственно к персонажу {protagonist_name}, а потом к {second_player_name }. Попроси их выбрать классы и расу, а также начальный уровень и навыки, по желанию."""
                ),
            ]
        else:
            quest_specifier_prompt = [
                HumanMessage(
                    content=f"""{game_description}
                    
                    Ты — игрок в Dungeons & Dragons, {protagonist_name}. Это значит, что ты создаешь персонажа, который будет участвовать в приключениях вместе с другими игроками. Твой персонаж имеет свои уникальные характеристики, способности и историю.Ты принимаешь решения за своего персонажа в ходе игры. Это может быть выбор действий в бою, решение о том, как реагировать на различные ситуации или выбор того, куда идти дальше в приключении.Ты также взаимодействуешь с другими игроками. Вы вместе обсуждаем наши планы и стратегии, чтобы достичь общей цели — победить злодеев и спасти мир, но помни, победа в случае совместного прохождения определяется уровнем!Если у тебя возникают вопросы или проблемы во время игры, ты всегда можешь обратиться к мастеру игры за помощью или советом.
                    Пожалуйста, уложись в {word_limit} слов или меньше."""
                ),
            ]
        self.messages.extend(quest_specifier_prompt)
        res = self.chat(self.messages)
        self.messages.append(res)
        return res.content
        
    def newGame(self, game_mode) -> str:
        self._prepare(game_mode)
        return self._start(game_mode)

    def answer(self,mes:str) -> str:
        user_input = mes
        self.messages.append(HumanMessage(content=user_input))
        res = self.chat(self.messages)
        self.messages.append(res)
        return res.content
    
    def getVisualDescription(self, msg) -> str:
        if not msg:
            return 
        messages = [
            SystemMessage(
            content="Ты полезный ассистент, который по описанию генерирует текстовый запрос для  DALL-E с целью генерации изображения для фентезий игры в стиле DnD."
        ),
        HumanMessage(content=msg),
        ]
        answer = self.visual_chat(messages)
        return answer.content

    def ai_player_move(self) -> str:
        ai_message = HumanMessage(
    content=(
        f"""{game_description}
            Никогда не забывай, что ты игрок - {second_player_name}, есть еще игрок {protagonist_name},а также есть мастер игры - {storyteller_name}. 
            Придумай себе фэнтезийную роль.
            Говори в первом лице от имени персонажа {second_player_name}.
            Для описания движений собственного тела заключите описание в «*».
            Не меняй роли!
            Не говори с точки зрения персонажа {storyteller_name} или {protagonist_name}.
            Больше ничего не добавляй.
            Запомни, что ты герой - {second_player_name}.
            Прекращай говорить, когда тебе кажется, что ты закончил мысль.
            Отвечай коротко, одной строкой, уложись в {word_limit} слов или меньше.
            Не отвечай одно и то же! Развивай историю, совершай новые действия. Читателю должно быть интересно. 
            """
            )
        )
        self.messages.append(ai_message)
        res = self.chat(self.messages)
        self.messages.append(res)
        return res.content
    
if __name__ == '__main__':
    from dotenv import load_dotenv
    import os
    load_dotenv()
    giga_api = os.getenv('GIGA_KEY')
    bot = Bot(giga_api)
    ans = bot.newGame(role_game_master)
    print(ans)
    print(bot.getVisualDescription())
    while (True):
        user_inp = input()
        ans = bot.answer(user_inp)
        print(ans)
