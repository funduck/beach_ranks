# beach_ranks

сводка измышлений на тему и повод начать разговор  
и поможет нам не забывать всякое

## Этапы проекта
1) чат бот  
2) сайтик со статами  
3) моб. приложение (когда-нибудь)  

## Команды чат бота  
вкратце  
* nick  - добавить ник, по которому бот будет тебя знать  
* forget  - убрать ник  
* team  - создать команду   
* split  - разбить команду  
* game  - запись результатов игры  
* player - получить инфу про игрока
* list games  - вывод списка игр  
* list teams  - вывод списка команд  
* help  - справка  

далее подробнее о каждой команде  
### nick 
`nick fanduck` - и бот знает меня теперь под таким именем  
### forget  
`forget fanduck` - и я больше не фандук  
### team  
возвращает `id` команды  
* 1 агрумент - `team kinkreet` - и я в команде с kinkreet  
* 2 аргумента - `team PRODAZHA XPEHOPE3` - и продажа играет вместе с хренорезом  
### split  
* 1 аргумент - `split tonya` - если больше не играешь с tonya  
* 1 агрумент `id` - `split 342346` - разобрать команду
* 2 агрумента - `split vasya sanek` - и этой пары больше нет  
### game  
возможно несколько вариантов:  
* `game mazi oleg grisha tonya 12 15` - полное описание  
* `game mazi grisha tonya 12 15` - может означать то же самое, если до этого было `team oleg mazi`  
* `game oleg grisha tonya 12 15` - аналогично  
* `game mazi grisha 12 15` - если до этого было `team oleg mazi` и `team grisha tonya`
* `game mazi tonya 12 15` - аналогично, ну и остальные 2 варианта тоже возможны  

команда возвращает `id` игры, по которому можно тоже кое-что сделать:  
* game 984723 14 16` - изменить результат  
* game 984723 cancel` - отменить  
### player
1 аргумент имя или телефон  
* player nick  
* player 79025154368

### list games
просмотреть список игр, по-умолчанию за последний час например  
* `list games` - все  
* `list games my` - все мои  
* `list games mazi` - игры mazi  

в выводе первым идет тот самый `id` игр  
### list teams
просмотреть список команд  
* `list teams` - все  
* `list teams my` - все мои  
* `list teams mazi` - в которых mazi  

в выводе первым идет тот самый `id` команды  
### help
ну понятно, справку выдает  
