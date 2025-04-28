from pyllist import sllist, sllistnode      # Vienakryptis tiesinis sarasas ir jo mazgai
from collections import deque               # Eile
import PySimpleGUI as sg                    # UI
import json                                 # DZEISONAS
from datetime import datetime, timedelta    # Datu formatavimas, veiksmai, lyginimai ir t.t.

task_list = sllist() # Inicijuojamas VTS

# VTS IRASYMAS I JSON
def saveTasksJSON(task_list, filename):
    data = [node for node in task_list]
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# VTS IRASYMAS IS JSON
def loadTasksJSON(task_list, filename):
    
    json_string = "[]"
    data = json.loads(json_string)
    if not data:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            for task in data:
                node = sllistnode(task)  
                task_list.appendright(node)  
    else:
        print("JSON empty.")

# TASKS GAVIMAS INTERFACE'UI (weekOnly, tai nusako ar reikia gauti tik sios savaites uzduotis) #NO ITERATION FIX
def getTasks(task_list, weekOnly):
    tasks = []
    count = 0
    if weekOnly:
        currentDatetime = datetime.now()
        currentDate = currentDatetime.date()
        startOfWeek = currentDate - timedelta(days=currentDate.weekday())  
        endOfWeek = startOfWeek + timedelta(days=6)         
        while count < task_list.size:
            task = task_list.nodeat(count)
            task_data = task.value
            task_deadline = task_data["deadline"]            
            task_real_deadline = datetime.strptime(task_deadline, "%Y-%m-%d %H:%M")            
            if startOfWeek <= task_real_deadline.date() <= endOfWeek:
               tasks.append(task_data)
            count += 1       
    else:
        while count < task_list.size:
            task = task_list.nodeat(count)
            task_data = task.value
            tasks.append(task_data)
            count += 1
    return tasks    
    
# Uzduoties pridejimo i pozicija funkcija, naudoja SLLIST biblioteka (nera addToPosition), pati labiau reikalinga duomenu formatavimui #NO ITERATION FIX
def addTaskPosition(task_list, position, name, subject, deadline, dayOfWeek, note, misc=None):
    task = sllistnode({
        "id" : position,
        "name": name,
        "subject": subject,
        "deadline": deadline,
        "dayOfWeek": dayOfWeek,
        "note": note,
        "misc": misc
    })
    new_task = task

    if position == 'end':
        task_list.appendright(new_task) #Dedam i pati gala po desine
    elif position <= 0 or task_list.first is None:
        task_list.appendleft(new_task) #Dedam i pati prieki po kaire
        
    # Realus idejimas i pozicija, naudojami pyllist metodai (ideda tiesiai i ta pozicija, jei irasai 5 tai ides po 4 ir t.t.)
    else:
        count = 0
        current_node = task_list.first
        while count < position:
            current_node = current_node.next
            count += 1
        task_list.insert(new_task, current_node)
      
 # Poziciju priskyrimas (ID), reikia atlikti po kiekvieno VTS modifikavimo
def positioning(task_list):
    position = 0
    current_node = task_list.first    
    while current_node is not None:
        current_node.value["id"]  = position 
        position += 1
        current_node = current_node.next

# Eiles klase, nes moddint reikia is deko
class queue:
    def initialize (self):
        self.queue = deque()
        
    def enqueue(self, task):
        self.queue.append(task)
        
    def dequeue(self):
        return self.queue.popleft()
       
    def is_empty(self):
        if len(self.queue) == 0:
            return True
        else:
            return False
        
    def peek(self):
        return self.queue[0]
    
    def size(self):
        return len(self.queue)

def getFoundTasks (foundTasks):
    tasks = []
    saving = queue()
    saving.initialize()
    while not foundTasks.is_empty():
        saving.enqueue(foundTasks.peek())
        foundTasks.dequeue()
        
    while not saving.is_empty():
        tasks.append(saving.peek())
        foundTasks.enqueue(saving.peek())
        saving.dequeue()
        
    del saving
    return tasks
        
def findNode (task_list, id):
    current_node = task_list.first
    while current_node.value['id'] != id:
        current_node = current_node.next
    return current_node    

def get_tail(head):
    while head and head.next:
        head = head.next
    return head

def partition(head, end):
    pivot = end.value
    pivot_prev = head
    current = head
    pivot_node = end
    
    while head != end:
        hihi = datetime.strptime(head.value["deadline"], "%Y-%m-%d %H:%M")
        haha = datetime.strptime(pivot["deadline"], "%Y-%m-%d %H:%M")
        if hihi < haha:
            pivot_prev = current
            current.value, head.value = head.value, current.value
            current = current.next
        head = head.next
    
    current.value, end.value = end.value, current.value
    
    return pivot_prev

def quick_sort_rec(first, last):
    if not first or first == last or first == last.next:
        return
    
    pivot_prev = partition(first, last)
    
    quick_sort_rec(first, pivot_prev)
    
    if pivot_prev and pivot_prev.next:
        quick_sort_rec(pivot_prev.next.next, last)

def quick_sort(linked_list):
    if not linked_list.first:
        return
    
    tail = get_tail(linked_list.first)
    quick_sort_rec(linked_list.first, tail)











loadTasksJSON(task_list, 'Tasks.json')
positioning(task_list)













# Pagrindinis ciklas:
running = True
while running:
    # PAGRINDINIS MENIU

    tasks = getTasks(task_list, True)
    homeLayout = [  [sg.Text('Upcomming tasks this week:')]   ]            
    if not tasks: 
        homeLayout.append([sg.Text('No tasks!!! RELAX')])
    else:              
        task_row = []
        for task in tasks:
            title_text = f"{task['name']}       ID: {task['id']}"
            task_frame = sg.Frame(
                title=title_text,
                layout=[
                    [sg.Text(f'Subject: {task["subject"]}')],
                    [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                    [sg.Text(f'Note: {task["note"]}')],
                    [sg.Text(f'Misc: {task["misc"]}')]
                ],
                expand_x=True,
                relief=sg.RELIEF_SOLID
            )
            task_row.append(task_frame)                     
        homeLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])                
    homeLayout.append([sg.Button('All tasks')])
    homeLayout.append([sg.Button('Add tasks')])
    homeLayout.append([sg.Button('Search tasks')])
    homeLayout.append([sg.Button('Sort tasks by deadline')])
    homeLayout.append([sg.Button('Quit')])
    homeWindow = sg.Window("Best Task Manager", homeLayout)
    
    # PAGRINDINIO MENIU CIKLAS
    while True:
        event, values = homeWindow.read()
        # QUIT MENIU
        if event == sg.WIN_CLOSED or event == "Quit":
            print("Quit attempt")#Logging
            homeWindow.close() # PAGRINDINIO MENIU CLOSE
            quitLayout = [
                [sg.Text('Do you really want to QUIT the BEST TASK MANAGER?')],
                [sg.Button('Yes -_-`'), sg.Button('No ^_^')]
            ]
            quitWindow = sg.Window('Best Task Manager', quitLayout)
            # QUIT MENIU CIKLAS
            while True:
                event, values = quitWindow.read()
                # QUIT 
                if event == 'Yes -_-`':
                    print('Goodbye')#Logging
                    running = False
#<------------------^^^^^^^^^^^^^^^                    
                    quitWindow.close()
                    break
            #<------^^^^^        
                # BACK to PAGRINDINIS MENIU    
                if event == sg.WIN_CLOSED or event == 'No ^_^':
                    print('Very nice! :)')#Logging
                    quitWindow.close()
                    break
            #<------^^^^^    
            break
    #<------^^^^^
        
        # ALL TASKS MENIU
        if event == 'All tasks':
            print('All tasks')
            homeWindow.hide() # PAGRINDINIO MENIU HIDE
            
            tasks = getTasks(task_list, False)
            allTasksLayout = [  [sg.Text('All upcomming tasks:')]   ]           
            if not tasks: 
                allTasksLayout.append([sg.Text('No tasks!!! RELAX')])
            else:              
                task_row = []
                for task in tasks:
                    title_text = f"{task['name']}       ID: {task['id']}"
                    task_frame = sg.Frame(
                        title=title_text,
                        layout=[
                            [sg.Text(f'Subject: {task["subject"]}')],
                            [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                            [sg.Text(f'Note: {task["note"]}')],
                            [sg.Text(f'Misc: {task["misc"]}')]
                        ],
                        expand_x=True,
                        relief=sg.RELIEF_SOLID
                    )
                    task_row.append(task_frame)                      
                allTasksLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])                
            allTasksLayout.append([sg.Button('Back')])
            allTasksWindow = sg.Window('Best Task Manager', allTasksLayout)
            
            # ALL TASKS MENIU CIKLAS
            while True:
                event, values = allTasksWindow.read()
                # BACK to PAGRINDINIS MENIU
                if event == sg.WIN_CLOSED or event == 'Back':
                    print('Back from All tasks')
                    allTasksWindow.close()
                    break
            #<------^^^^^
            break
    #<------^^^^^    
         
        # ADD TASKS MENIU
        if event == 'Add tasks':
            print('Add tasks')#Logging
            homeWindow.hide() # PAGRINDINIO MENIU HIDE
            
            tasks = getTasks(task_list, False)
            addTasksLayout = [  [sg.Text('All upcomming tasks:')]   ]            
            if not tasks: 
                addTasksLayout.append([sg.Text('No tasks!!! RELAX')])
            else:             
                task_row = []
                for task in tasks:
                    title_text = f"{task['name']}       ID: {task['id']}"
                    task_frame = sg.Frame(
                        title=title_text,
                        layout=[
                            [sg.Text(f'Subject: {task["subject"]}')],
                            [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                            [sg.Text(f'Note: {task["note"]}')],
                            [sg.Text(f'Misc: {task["misc"]}')]
                        ],
                        expand_x=True,
                        relief=sg.RELIEF_SOLID
                    )
                    task_row.append(task_frame)                      
                addTasksLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])                          
            addTasksLayout.append([sg.Text('Position:'), sg.InputText()])
            addTasksLayout.append([sg.Text('Name:    '), sg.InputText()])
            addTasksLayout.append([sg.Text('Subject: '), sg.InputText()])
            addTasksLayout.append([sg.Text('Deadline:'), sg.InputText()])
            addTasksLayout.append([sg.Text('Note:     '), sg.InputText()])
            addTasksLayout.append([sg.Text('Misc:      '), sg.InputText()])
            addTasksLayout.append([sg.Button('Back'), sg.Button('Add')])
            addTasksLayout.append([sg.Text('● Position - Before which task (ID) new task should be inserted, also could be `end` (default = 0)')])
            addTasksLayout.append([sg.Text('                 Examples: 5 - task added to 5th position')])
            addTasksLayout.append([sg.Text('                                  0 - task added to the first position')])
            addTasksLayout.append([sg.Text('                                  end - task added to the last position')])
            addTasksLayout.append([sg.Text('                 Scenario: List: 1 2 3 -> add to position 2 -> List: 1 2(new) 3 4')])
            addTasksLayout.append([sg.Text('● Name - Recommended to use consistent and formal task names for better managing')])
            addTasksLayout.append([sg.Text('                 Examples: Homework / Exam / Midterm')])
            addTasksLayout.append([sg.Text('● Subject - Recommended to use consistent and formal task subjects for better managing')])
            addTasksLayout.append([sg.Text('                 Examples: Mathematical Analysis / ADS / Computer Networks')])
            addTasksLayout.append([sg.Text('● Deadline - Cannot be expired at the time of adding the task')])
            addTasksLayout.append([sg.Text('                 Format: YYYY-MM-DD HH:MM')])
            addTasksLayout.append([sg.Text('                 Example: 2004-08-30 21:46')])
            addTasksLayout.append([sg.Text('● Note - Explanation or a specification of the task, creativity here is unrestricted')])
            addTasksLayout.append([sg.Text('○ Misc (Optional) - Information that does NOT fit any of the other fields, could be whatever you imagine')])
            addTasksWindow = sg.Window('Best Task Manager', addTasksLayout)
            
            # ADD TASKS MENIU CIKLAS
            while True:
                event, values = addTasksWindow.read()
                # BACK to PAGRINDINIS MENIU
                if event == sg.WIN_CLOSED or event == 'Back':
                    print('Back from Add tasks')#Logging
                    addTasksWindow.close() # ADD TASKS MENIU CLOSE
                    break
            #<------^^^^^    
                # ADD TASK 
                if event == 'Add':
                    print('Add task executing')#Logging

                    position = values[0] if values[0] else "0"
                    name = values[1] if values[1] else "null"
                    subject = values[2] if values[2] else "null"
                    deadline = values[3] if values[3] else "null"
                    note = values[4] if values[4] else "null"
                    misc = values[5] if values[5] else None
                    
                    print(position)#Logging
                    print(name)#Logging
                    print(subject)#Logging
                    print(deadline)#Logging
                    print(note)#Logging
                    print(misc)#Logging

                    nullInput_Error = False
                    nullInput_ErrorCode = 'Please fill out following field(s):\n'
                    if name == "null":
                        nullInput_Error = True
                        nullInput_ErrorCode += "| Name |\n"
                    if subject == "null":
                        nullInput_Error = True
                        nullInput_ErrorCode += "| Subject |\n"
                    if deadline == "null":
                        nullInput_Error = True
                        nullInput_ErrorCode += "| Deadline |\n"
                    if note == "null":
                        nullInput_Error = True
                        nullInput_ErrorCode += "| Note |\n"    

                    formatInput_Error = False
                    deadlineSpecific = False
                    positionSpecific = False
                    formatInput_ErrorCode = 'Wrong format in following field(s):\n'                    
                    if position.isdigit() or position == "end":                        
                        positionSpecific = False #nieko nedaro
                    else:
                       formatInput_Error = True
                       positionSpecific = True
                       formatInput_ErrorCode += "| Position format is only a integer or `end` |\n"
                    if len(name) < 2 and name != "null":
                        formatInput_Error = True
                        formatInput_ErrorCode += "| Name cannot be 1 letter |\n"
                    if len(subject) < 2 and subject != "null":
                        formatInput_Error = True
                        formatInput_ErrorCode += "| Subject cannot be 1 letter |\n" 
                    if deadline != "null":    
                        try:
                            formatted_deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                            dayOfWeek = formatted_deadline.strftime("%A")
                        except ValueError:
                            formatInput_Error = True
                            deadlineSpecific = True
                            formatInput_ErrorCode += "| Deadline format is YYYY-MM-DD HH:MM |\n"
                    if len(note) < 2 and note != "null":
                        formatInput_Error = True
                        formatInput_ErrorCode += "| Note cannot be 1 letter |\n"
                        
                    logicInput_Error = False
                    logicInput_ErrorCode = "Logic issues in following field(s):\n"
                    if position != "end" and position != "null" and positionSpecific == False:
                        position = int(position)
                        if position > task_list.size and position != 0:
                            logicInput_ErrorCode += "| Position is out of bounds |\n"
                            logicInput_Error = True
                    if deadline != "null" and deadlineSpecific == False:
                        current_time = datetime.now()
                        if formatted_deadline < current_time:
                            logicInput_Error = True
                            logicInput_ErrorCode += "| Deadline cannot be expired |\n"
                    print(nullInput_ErrorCode)#Logging
                    print(formatInput_ErrorCode)#Logging
                    print(logicInput_ErrorCode)#Logging
                    errorString = ''
                    if(nullInput_Error or formatInput_Error or logicInput_Error):
                        addTasksWindow.hide()
                        addTasksErrorLayout = [[sg.Text('ERRORS!')]]
                        if(nullInput_Error):
                            errorString += nullInput_ErrorCode + '\n'
                        if(formatInput_Error):
                            errorString += formatInput_ErrorCode + '\n'  
                        if(logicInput_Error):
                            errorString += logicInput_ErrorCode + '\n'

                        sg.popup(errorString, title="OOPS..")
                        addTasksWindow.un_hide()

                    else:
                        addTaskPosition(task_list, position, name, subject, deadline, dayOfWeek, note, misc)
                        positioning(task_list)
                        saveTasksJSON(task_list, 'Tasks.json')
                        addTasksWindow.close()
                        succesfulAddLayout = [[sg.Text('Task Added!')],
                                              [sg.Button('OK')]]
                        succesfulAddWindow = sg.Window('Best Task Manager', succesfulAddLayout)
                        while True:
                            event, values = succesfulAddWindow.read()
                            if event == sg.WIN_CLOSED or event == 'OK':
                                succesfulAddWindow.close() # ADD TASKS MENIU CLOSE
                                homeWindow.close()
                                break
                        #<------^^^^^
            break
    #<------^^^^^ 

        # SEARCH TASKS MENIU
        if event == 'Search tasks':
            print('Search tasks')
            homeWindow.hide() # PAGRINDINIO MENIU HIDE
            
            tasks = getTasks(task_list, False)
            searchTasksLayout = [  [sg.Text('All upcomming tasks:')]   ]            
            if not tasks: 
                searchTasksLayout.append([sg.Text('No tasks!!! RELAX')])
            else:              
                task_row = []
                for task in tasks:
                    title_text = f"{task['name']}       ID: {task['id']}"
                    task_frame = sg.Frame(
                        title=title_text,
                        layout=[
                            [sg.Text(f'Subject: {task["subject"]}')],
                            [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                            [sg.Text(f'Note: {task["note"]}')],
                            [sg.Text(f'Misc: {task["misc"]}')]
                        ],
                        expand_x=True,
                        relief=sg.RELIEF_SOLID
                    )
                    task_row.append(task_frame)                      
                searchTasksLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])
            searchTasksLayout.append([sg.Text('*Name or Subject'), sg.InputText()])
            searchTasksLayout.append([sg.Text('Search by:'), sg.Button('Name'), sg.Button('Subject')])
            searchTasksLayout.append([sg.Button('Back')])            
            searchTasksWindow = sg.Window('Best Task Manager', searchTasksLayout)

            category = 'unknown'    # Isaugos pagal ka ieskos (Name/Subject)
            found = False           # Jei bus rasta TRUE, jei ne - FALSE dialogo zinutei
            moreThanOne = False     # Jei bus rasta daugiau nei viena uzd. bus papildomas specifikavimo meniu
            wasMorethanOne = False  # Jei bus griztama, kad atgal uzsuktu ir paplidoma specifikavimo meniu ^

            # SEARCH TASKS MENIU CIKLAS
            while True:
                event, values = searchTasksWindow.read()
                # BACK to PAGRINDINIS MENIU
                if event == sg.WIN_CLOSED or event == 'Back':
                    print('Back from Search tasks')#Logging
                    searchTasksWindow.close() # SEARCH TASKS MENIU CLOSE
                    homeWindow.un_hide()
                    break
            #<------^^^^^

                # SEARCH by NAME
                if event == 'Name':
                    print('Search by Name executing')#Logging
                    searchTasksWindow.hide() # SEARCH TASKS MENIU CLOSE
                    category = 'name'

                # SEARCH by SUBJECT
                if event == 'Subject':
                    print('Search by Subject executing')#Logging
                    searchTasksWindow.hide() # SEARCH TASKS MENIU CLOSE
                    category = 'subject'
                    
                # SEARCH BY X KODA DETI CIA <<<---
                criteria = values[0] if values[0] else "null"
                if criteria == "null":
                    sg.popup("DO NOT LEAVE THE FIELD BLANK")
                foundTasks = queue()
                foundTasks.initialize()
                current_node = task_list.first
                while current_node is not None:
                    if current_node.value[category] == criteria:
                        foundTask = current_node.value
                        foundTasks.enqueue(foundTask)
                    current_node = current_node.next    
                if foundTasks.is_empty():
                    found = False
                    sg.popup(f"No Task with {criteria} {category} exists!")
                    searchTasksWindow.un_hide()
                elif foundTasks.size() == 1:
                    found = True
                    moreThanOne = False
                    wasMorethanOne = False
                    specified = True
                else:
                    found = True
                    moreThanOne = True
                    wasMorethanOne = True
                    
                # AFTER SEARCH CIKLAS
                while found:
                    print('found by: ' + category)#Logging
                    searchTasksWindow.hide()
                    # MULTIPLE FOUND, SPECIFY TASK MENIU
                    if moreThanOne == True and wasMorethanOne == True:
                        print('found multiple')#Logging
                        
                        tasks = getFoundTasks(foundTasks)  
                        specifySearchLayout = [  [sg.Text('Multiple tasks found by specified ' + category + ": " + criteria)]   ]            
                        if not tasks: 
                            specifySearchLayout.append([sg.Text('No tasks?')])
                        else:              
                            task_row = []
                            for task in tasks:
                                title_text = f"{task['name']}       ID: {task['id']}"
                                task_frame = sg.Frame(
                                    title=title_text,
                                    layout=[
                                        [sg.Text(f'Subject: {task["subject"]}')],
                                        [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                                        [sg.Text(f'Note: {task["note"]}')],
                                        [sg.Text(f'Misc: {task["misc"]}')]
                                    ],
                                    expand_x=True,
                                    relief=sg.RELIEF_SOLID
                                )
                                task_row.append(task_frame)                      
                            specifySearchLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])
                            specifySearchLayout.append([sg.Text('Specify exact task ID:'), sg.InputText()])
                            specifySearchLayout.append([sg.Button('Back'), sg.Button('Search')])

                        specifySearchWindow = sg.Window('Best Task Manager', specifySearchLayout)
                        # SPECIFY TASK MENIU CIKLAS
                        while True:
                            event, values = specifySearchWindow.read()
                            # BACK to SEARCH TASKS MENIU
                            if event == sg.WIN_CLOSED or event == 'Back':
                                print('Back from Specify search')#Logging
                                specifySearchWindow.close() # SPECIFY SEARCH MENIU CLOSE
                                # Variable reset
                                category = 'unknown'
                                found = False
                                moreThanOne = False
                                wasMorethanOne = False
                                searchTasksWindow.un_hide()
                                break
                        #<------^^^^^
                            # SEARCH SPECIFICATION by ID
                            if event == 'Search':
                                print('Specify search executing')#Logging
                                # SPECIFY SEARCH BY ID KODA DETI CIA <<<---
                                specified = False
                                ID = int(values[0])
                                savingAll = queue()
                                savingAll.initialize()
                                while not foundTasks.is_empty():
                                    savingAll.enqueue(foundTasks.peek())
                                    if foundTasks.peek()['id'] == ID:
                                        task = foundTasks.peek()
                                        specified = True
                                    foundTasks.dequeue()
                                if specified:                                    
                                    foundTasks.enqueue(task)
                                    moreThanOne = False
                                else:
                                    sg.popup(f"No Task with {ID} ID exists with {category} {criteria}!")
                                    specifySearchWindow.close()
                                    while not savingAll.is_empty():
                                        foundTasks.enqueue(savingAll.peek())
                                        savingAll.dequeue()

                                break
                        #<------^^^^^
                         
                    # ONE FOUND or SPECIFIED ALREADY MENIU
                    if moreThanOne == False and specified == True and found == True:
                        print("task found")#Logging
                        if wasMorethanOne:
                            specifySearchWindow.close()
                        else:    
                            searchTasksWindow.hide()
                        tasks = getFoundTasks(foundTasks)
                        taskFoundLayout = [  [sg.Text('Task found by specified ' + category + ": " + criteria)]   ]            
                        if not tasks: 
                            taskFoundLayout.append([sg.Text('No task?')])
                        else:              
                            task_row = []
                            for task in tasks:
                                title_text = f"{task['name']}       ID: {task['id']}"
                                task_frame = sg.Frame(
                                    title=title_text,
                                    layout=[
                                        [sg.Text(f'Subject: {task["subject"]}')],
                                        [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                                        [sg.Text(f'Note: {task["note"]}')],
                                        [sg.Text(f'Misc: {task["misc"]}')]
                                    ],
                                    expand_x=True,
                                    relief=sg.RELIEF_SOLID
                                )
                                task_row.append(task_frame)                      
                            taskFoundLayout.append([sg.Column([task_row], expand_x=True)])
                            taskFoundLayout.append([sg.Button('Modify'), sg.Button('Delete')])
                            taskFoundLayout.append([sg.Button('Back')])

                        taskFoundWindow = sg.Window('Best Task Manager', taskFoundLayout)

                        # ONE FOUND or SPECIFIED ALREADY MENIU CIKLAS
                        while True:
                            event, values = taskFoundWindow.read()
                            # BACK to SEARCH MENIU or SPECIFICATION MENIU
                            if event == sg.WIN_CLOSED or event == 'Back':
                                print('Back from Task found')
                                taskFoundWindow.close()
                                if wasMorethanOne:
                                    moreThanOne = True
                                    specified = False
                                    while not foundTasks.is_empty():
                                        foundTasks.dequeue()
                                    while not savingAll.is_empty():
                                        foundTasks.enqueue(savingAll.peek())
                                        savingAll.dequeue()
                                    del savingAll                                    
                                else:    
                                    searchTasksWindow.un_hide()
                                    found = False
                                break
                        #<------^^^^^
                            # MODIFY SELECTED TASK MENIU
                            if event == 'Modify':
                                print('Modify initalized')
                                IDtoMod = foundTasks.peek()['id']
                                nodeToMod = findNode(task_list, IDtoMod)
                                nodePreview = nodeToMod.value

                                taskModifyLayout = [    
                                    [sg.Text(f'Position: {nodePreview["id"]} Change to:'), sg.InputText(key='-POSITION-')],
                                    [sg.Text(f'Name: {nodePreview["name"]} Change to:'), sg.InputText(key='-NAME-')],
                                    [sg.Text(f'Subject: {nodePreview["subject"]} Change to:'), sg.InputText(key='-SUBJECT-')],
                                    [sg.Text(f'Deadline: {nodePreview["deadline"]} Change to:'), sg.InputText(key='-DEADLINE-')],
                                    [sg.Text(f'Note: {nodePreview["note"]} Change to:'), sg.InputText(key='-NOTE-')],
                                    [sg.Text(f'Misc: {nodePreview["misc"]} Change to:'), sg.InputText(key='-MISC-')],
                                    [sg.Button('Back'), sg.Button('Done')]
                                ]
                                taskModifyLayout.append([sg.Text('● Position - Before which task (ID) new task should be inserted, also could be `end`')])
                                taskModifyLayout.append([sg.Text('                 Examples: 5 - task added to 5th position')])
                                taskModifyLayout.append([sg.Text('                                  0 - task added to the first position')])
                                taskModifyLayout.append([sg.Text('                                  end - task added to the last position')])
                                taskModifyLayout.append([sg.Text('                 Scenario: List: 1 2 3 -> add to position 2 -> List: 1 2(new) 3 4')])
                                taskModifyLayout.append([sg.Text('● Name - Recommended to use consistent and formal task names for better managing')])
                                taskModifyLayout.append([sg.Text('                 Examples: Homework / Exam / Midterm')])
                                taskModifyLayout.append([sg.Text('● Subject - Recommended to use consistent and formal task subjects for better managing')])
                                taskModifyLayout.append([sg.Text('                 Examples: Mathematical Analysis / ADS / Computer Networks')])
                                taskModifyLayout.append([sg.Text('● Deadline - Cannot be expired at the time of adding the task')])
                                taskModifyLayout.append([sg.Text('                 Format: YYYY-MM-DD HH:MM')])
                                taskModifyLayout.append([sg.Text('                 Example: 2004-08-30 21:46')])
                                taskModifyLayout.append([sg.Text('● Note - Explanation or a specification of the task, creativity here is unrestricted')])
                                taskModifyLayout.append([sg.Text('○ Misc (Optional) - Information that does NOT fit any of the other fields, could be whatever you imagine')])
                                taskModifyWindow = sg.Window('Best Task Manager', taskModifyLayout)

                                # MODIFY SELECTED TASK MENIU CIKLAS
                                while True:
                                    event, values = taskModifyWindow.read()
                                    
                                    # BACK to ONE FOUND or SPECIFIED ALREADY MENIU
                                    if event == sg.WIN_CLOSED or event == 'Back':
                                        print('Back from Task modify')
                                        taskModifyWindow.close()
                                        break
                                #<------^^^^^

                                    if event == 'Done':
                                        print('Modifications init')
                                        position = values['-POSITION-'] if values['-POSITION-'] else "null"
                                        name = values['-NAME-'] if values['-NAME-'] else "null"
                                        subject = values['-SUBJECT-'] if values['-SUBJECT-'] else "null"
                                        deadline = values['-DEADLINE-'] if values['-DEADLINE-'] else "null"
                                        note = values['-NOTE-'] if values['-NOTE-'] else "null"
                                        misc = values['-MISC-'] if values['-MISC-'] else "null"
                                        if position == "null" and name == "null" and subject == "null" and deadline == "null" and note == "null" and misc == "null":
                                            sg.popup("Nothing changed!")
                                        else:
                                            formatInput_Error = False
                                            deadlineSpecific = False
                                            positionSpecific = False
                                            formatInput_ErrorCode = 'Wrong format in following field(s):\n'                    
                                            if position.isdigit() or position == "end" or position == "null":                        
                                                positionSpecific = False #nieko nedaro
                                            else:
                                               formatInput_Error = True
                                               positionSpecific = True
                                               formatInput_ErrorCode += "| Position format is only a integer or `end` |\n"
                                            if len(name) < 2 and name != "null":
                                                formatInput_Error = True
                                                formatInput_ErrorCode += "| Name cannot be 1 letter |\n"
                                            if len(subject) < 2 and subject != "null":
                                                formatInput_Error = True
                                                formatInput_ErrorCode += "| Subject cannot be 1 letter |\n" 
                                            if deadline != "null":    
                                                try:
                                                    formatted_deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
                                                    dayOfWeek = formatted_deadline.strftime("%A")
                                                except ValueError:
                                                    formatInput_Error = True
                                                    deadlineSpecific = True
                                                    formatInput_ErrorCode += "| Deadline format is YYYY-MM-DD HH:MM |\n"
                                            if len(note) < 2 and note != "null":
                                                formatInput_Error = True
                                                formatInput_ErrorCode += "| Note cannot be 1 letter |\n"
                        
                                            logicInput_Error = False
                                            logicInput_ErrorCode = "Logic issues in following field(s):\n"
                                            if position != "end" and position != "null" and positionSpecific == False:
                                                position = int(position)
                                                if position > task_list.size and position != 0:
                                                    logicInput_ErrorCode += "| Position is out of bounds |\n"
                                                    logicInput_Error = True
                                            if deadline != "null" and deadlineSpecific == False:
                                                current_time = datetime.now()
                                                if formatted_deadline < current_time:
                                                    logicInput_Error = True
                                                    logicInput_ErrorCode += "| Deadline cannot be expired |\n"
                                            print(formatInput_ErrorCode)#Logging
                                            print(logicInput_ErrorCode)#Logging
                                            errorString = ''
                                            error = False
                                            if(formatInput_Error or logicInput_Error):
                                                error = True
                                                addTasksErrorLayout = [[sg.Text('ERRORS!')]]
                                                if(formatInput_Error):
                                                    errorString += formatInput_ErrorCode + '\n'  
                                                if(logicInput_Error):
                                                    errorString += logicInput_ErrorCode + '\n'

                                                sg.popup(errorString, title="OOPS..")
                                         
                                            elif not error:
                                                if position != "null" and position != IDtoMod:
                                                    if name == "null":
                                                        name = nodePreview['name']
                                                    if subject == "null":
                                                        subject = nodePreview['subject']
                                                    if deadline == "null":
                                                        deadline = nodePreview['deadline']
                                                        dayOfWeek = nodePreview['dayOfWeek']
                                                    if note == "null":
                                                        note = nodePreview['note']
                                                    if misc == "null":
                                                        misc = nodePreview['misc']
                                                    foundTasks.dequeue()    
                                                    nodeToDelete = findNode(task_list, IDtoMod)
                                                    task_list.remove(nodeToDelete)
                                                    addTaskPosition(task_list, position, name, subject, deadline, dayOfWeek, note, misc)
                                                    positioning(task_list)
                                                    saveTasksJSON(task_list, 'Tasks.json')
                                                    if position == 'end':                                                        
                                                        position = task_list.size - 1

                                                    sg.popup("succesfull")
                                                    taskModifyWindow.close()
                                                    
                                                elif position == "null" or position == IDtoMod:
                                                    
                                                    if name != "null":
                                                        nodeToMod.value['name'] = name
                                                        
                                                    if subject != "null":
                                                        nodeToMod.value['subject'] = subject
                                                        
                                                    if deadline != "null":
                                                        nodeToMod.value['deadline'] = deadline
                                                        nodeToMod.value['dayOfWeek'] = dayOfWeek
                                                    if note != "null":
                                                        nodeToMod.value['note'] = note
                                                        
                                                    if misc != "null":
                                                        nodeToMod.value['misc'] = misc
                                                        
                                                    foundTasks.dequeue()   
                                                    sg.popup("succesfull")
                                                    taskModifyWindow.close()
                                                    saveTasksJSON(task_list, 'Tasks.json')
                                                    
                                                taskFoundWindow.close()
                                                moreThanOne = False
                                                specified = False                                 
                                                found = False          


                            # DELETE SELECTED TASK MENIU
                            if event == 'Delete':
                                print('Deleting executing')
                                IDtoDelete = foundTasks.peek()['id']
                                foundTasks.dequeue()
                                # DELETE SELECTED TASK KODA DETI CIA <<<---
                                nodeToDelete = findNode(task_list, IDtoDelete)
                                task_list.remove(nodeToDelete)
                                positioning(task_list)
                                saveTasksJSON(task_list, 'Tasks.json')
                                
                                sg.popup("Task deleted succesfully!")
                                if wasMorethanOne:
                                    specified = False
                                    while not foundTasks.is_empty():
                                        foundTasks.dequeue()
                                    while not savingAll.is_empty():
                                        if savingAll.peek()['id'] != IDtoDelete:
                                            foundTasks.enqueue(savingAll.peek())
                                        savingAll.dequeue()

                                    if foundTasks.size() <= 1:
                                        moreThanOne = False
                                        specified = True
                                        
                                else:    
                                    searchTasksWindow.close()
                                    taskFoundWindow.close()
                                    found = False
                                break
                        #<------^^^^^



        # SORT TASKS MENIU
        if event == 'Sort tasks by deadline':
            
            print('Sort tasks by deadline')
            homeWindow.close() # PAGRINDINIO MENIU CLOSE
    
            quick_sort(task_list)
            positioning(task_list)
            saveTasksJSON(task_list, 'Tasks.json')

            tasks = getTasks(task_list, False)
            sortTasksLayout = [  [sg.Text('All upcomming tasks:')]   ]           
            if not tasks: 
                sortTasksLayout.append([sg.Text('No tasks!!! RELAX')])
            else:              
                task_row = []
                for task in tasks:
                    title_text = f"{task['name']}       ID: {task['id']}"
                    task_frame = sg.Frame(
                        title=title_text,
                        layout=[
                            [sg.Text(f'Subject: {task["subject"]}')],
                            [sg.Text(f'Deadline: {task["deadline"]} {task["dayOfWeek"]}')],
                            [sg.Text(f'Note: {task["note"]}')],
                            [sg.Text(f'Misc: {task["misc"]}')]
                        ],
                        expand_x=True,
                        relief=sg.RELIEF_SOLID
                    )
                    task_row.append(task_frame)                      
                sortTasksLayout.append([sg.Column([task_row], scrollable=True, size=(500, 130), expand_x=True)])                
            sortTasksLayout.append([sg.Button('Back')])
            sortTasksWindow = sg.Window('Best Task Manager', sortTasksLayout)

            # SORT TASK MENIU CIKLAS
            while True:
                event, values = sortTasksWindow.read()
                # BACK to PAGRINDINIS MENIU
                if event == sg.WIN_CLOSED or event == 'Back':
                    print('Back from Add tasks')
                    sortTasksWindow.close() # SORT TASKS MENIU CLOSE
                    break
            #<------^^^^^    

            break
    #<------^^^^^                  