# -*- coding: utf-8 -*-
import tkinter, tkinter.messagebox, tkinter.filedialog
import PIL.Image, PIL.ImageTk
import omdb, requests, io, yaml, re, datetime

class FilmLogger(tkinter.Frame):
    '''Uses GUI to add entries to a FilmTrackr-compliant logging format

    Args:
        master (:obj:`tkinter.Tk`): tkinter object

    Attributes:
        master (:obj:`tkinter.Tk`): tkinter object
        archive (dict): working dictionary of logged entries

        file_select_button (:obj:`tkinter.Button`): button to trigger file_select function

        title_prompt (:obj:`tkinter.Label`): label to prompt entry of film title
        title_field (:obj:`tkinter.Entry`): field to enter film title

        day (:obj:`tkinter.IntVar`): int to store day of month film was seen
        day_prompt (:obj:`tkinter.Label`): label to prompt entry of day seen
        day_field (:obj:`tkinter.OptionMenu`): menu to pick day film seen

        month (:obj:`tkinter.IntVar`): int to store month of year film was seen
        month_prompt (:obj:`tkinter.Label`): label to prompt entry of month seen
        month_field (:obj:`tkinter.OptionMenu`): menu to pick month film seen

        year (:obj:`tkinter.IntVar`): int to store year film was seen
        year_prompt (:obj:`tkinter.Label`): label to prompt entry of year seen
        year_field (:obj:`tkinter.OptionMenu`): menu to pick year film seen

        theater_check (:obj:`tkinter.IntVar`): int to store if seen in a theater
        theater_check_button (:obj:`tkinter.CheckButton`): checkbox to select if seen in theater

        poster_image (:obj:`PIL.Image`): PIL image for poster of current film
        poster (:obj:`PIL.ImageTk.PhotoImage`): Tk PhotoImage for poster_image
        poster_label (:obj:`tkinter.Label`): label to show poster of film

        verified (bool): boolean value for verification status of film title
        verify_button (:obj:`tkinter.Button`): button to trigger verify function

        add_button (:obj:`tkinter.Button`): button to trigger add_entry function
        dump_button (:obj:`tkinter.Button`): button to trigger dump_file function
    '''
    def __init__(self, master):
        #intializes tkinter Frame and creates working directory for film entries
        self.master = master
        tkinter.Frame.__init__(self, master)
        self.archive = {}

        #button to trigger function to select and open a file
        self.file_select_button = tkinter.Button(master, text='Open File',command=self.file_select)
        self.file_select_button.grid(row=0,column=2)

        #label and field for entry of film title
        self.title_prompt = tkinter.Label(master, justify='left',text='Title: ')
        self.title_prompt.grid(row=1)
        self.title_field = tkinter.Entry(master)
        self.title_field.grid(row=1,column=1,columnspan=2,sticky='we')

        #creates day/month/year variables and sets their values to placeholders
        self.day, self.month, self.year = tkinter.IntVar(), tkinter.IntVar(), tkinter.IntVar()
        self.day.set('DD')
        self.month.set('MM')
        self.year.set('YYYY')

        #menu of valid calendar days in month
        #NOTE: month check TBA for valid day generation (i.e. block Feb 30)
        self.day_prompt = tkinter.Label(master, justify='center',text='Day: ')
        self.day_prompt.grid(row=2,column=0)
        self.day_field = tkinter.OptionMenu(master, self.day, *range(1,32))
        self.day_field.grid(row=3,column=0)

        #menu of valid calendar months in year
        self.month_prompt = tkinter.Label(master, justify='center',text='Month: ')
        self.month_prompt.grid(row=2,column=1)
        self.month_field = tkinter.OptionMenu(master, self.month, *range(1,13))
        self.month_field.grid(row=3,column=1)

        #menu of valid calendar years from 1 CE to the current year
        self.year_prompt = tkinter.Label(master, justify='center',text='Year: ')
        self.year_prompt.grid(row=2,column=2)
        self.year_field = tkinter.OptionMenu(master, self.year, *reversed(range(1,datetime.datetime.now().year+1)))
        self.year_field.grid(row=3,column=2)

        #value for whether film has been seen in theaters
        #IntVar required for tkinter Checkbutton, however in Python 1 == True &
        #0 == False. Slightly disgusting, but it works.
        self.theater_check = tkinter.IntVar()
        self.theater_check_button = tkinter.Checkbutton(master, text='Seen in theaters?',variable=self.theater_check)
        self.theater_check_button.grid(row=4, column=1)

        #sets the PIL image object to the default and halves the scale
        #image will be changed as verified films have posters pulled from IMDB
        self.poster_image = PIL.Image.open('default.jpg')
        self.poster_image = self.poster_image.resize((self.poster_image.size[0]//2,self.poster_image.size[1]//2), PIL.Image.ANTIALIAS)
        #creates Tk-compatible photoimage from poster_image, and places it into
        #label
        self.poster = PIL.ImageTk.PhotoImage(self.poster_image)
        self.poster_label = tkinter.Label(master, image=self.poster, borderwidth=0)
        self.poster_label.grid(row=0,column=3,rowspan=5)

        #button to trigger verification function
        self.verified = False
        self.verify_button = tkinter.Button(master, text='Verify',command=self.verify)
        self.verify_button.grid(row=4,column=2)

        #button to trigger function to add a new entry
        self.add_button = tkinter.Button(master, text='Add to archive',command=self.add_entry)
        self.add_button.grid(row=5,column=0,columnspan=5,sticky = 'we')

        #button to trigger function to dump archive to a static file
        self.dump_button = tkinter.Button(master, text='Dump to file',command=self.dump_file)
        self.dump_button.grid(row=6,column=0,columnspan=5,sticky = 'we')

    def file_select(self):
        '''Grabs a preexisting log file and adds it to the working archive

        Attributes:
            file_path (str): path to the selected file
            file_select_text (:obj:`tkinter.Label`): label to display file name
        '''
        #opens a filedialog that asks for a file with JSON or YAML formatting
        file_path = tkinter.filedialog.askopenfilename(filetypes=[('JSON/YAML','*.json;*.yml')])

        #opens the file into the working archive
        with open(file_path, 'r') as file:
            self.archive = yaml.load(file)

        #creates label showing the file's name
        #regex pulls the name from the file path by matching the last f-slash
        file_select_text = tkinter.Label(self.master, justify='left', text=re.findall(r'.+/(.+)', file_path)[0])
        file_select_text.grid(row=0,column=1)

    def verify(self):
        '''Verifies with IMDB that the film exists

        Attributes:
            film (dict): dictionary of attributes for the film to be verified
        '''
        #grabs & parses the JSON doc for the title, using the OMDBAPI wrapper
        film = omdb.title(self.title_field.get())

        #if the length of the attributes dict is non-zero (i.e. the film exists)
        if len(film) > 0:
            #points object poster_image to new PIL Image opened from bytestream
            #obtained using a GET request
            self.poster_image = PIL.Image.open(io.BytesIO(requests.get(film['poster']).content))
            self.poster_image = self.poster_image.resize((self.poster_image.size[0]//2,self.poster_image.size[1]//2), PIL.Image.ANTIALIAS)
            #points poster to new PhotoImage generated from new poster_image
            self.poster = PIL.ImageTk.PhotoImage(self.poster_image)
            #points poster_lable to new poster
            self.poster_label.configure(image=self.poster)

            #notifies user that the film has been verified
            tkinter.messagebox.showinfo('Verification Status','This film exists!')
            self.verified = True
        else:
            #notifies user that the film does not exist
            tkinter.messagebox.showerror('Verification Status','That film does not exist')
            self.verified = False

    def add_entry(self):
        '''Adds user entry to the working archive

        '''
        if self.verified:
            try:
                #adds entry to end of archive using the data from the fields
                self.archive[str(len(self.archive) + 1)] = {'Title':self.title_field.get(),
                'Day':self.day.get(),
                'Month':self.month.get(),
                'Year':self.year.get(),
                'Theater?':{1:'y',0:'n'}[self.theater_check.get()]}

                #notifies user that the film has been added to the archive
                tkinter.messagebox.showinfo('Entry Added','This film-watching experience has been added to your working archive. Remember to dump your archive after all new entries have been added!')

                #resets all fields and images to default values
                self.title_field.delete(0,'end')
                self.day.set('DD')
                self.month.set('MM')
                self.year.set('YYYY')
                self.theater_check.set(0)
                self.poster_image = PIL.Image.open('default.jpg')
                self.poster_image = self.poster_image.resize((self.poster_image.size[0]//2,self.poster_image.size[1]//2), PIL.Image.ANTIALIAS)
                self.poster = PIL.ImageTk.PhotoImage(self.poster_image)
                self.poster_label.configure(image=self.poster)
            except tkinter.TclError:
                #throws error when the day/month/year aren't an interger value,
                #such as when the user hasn't changed the placeholders
                tkinter.messagebox.showerror('Data Entry Error','That date is invalid. Ensure you have picked numbers for all the fields.')
        else:
            #notifies user that the film must be verified by IMDB to proceed
            tkinter.messagebox.showerror('Verification Error','This film has not been verified. Please verify your film to ensure it exists on IMDB.')

    def dump_file(self):
        '''Dumps working archive to static file

        Attributes:
            file_path (str): file path to create archive dump at
        '''
        #opens a filedialog promping user to set file location and name
        #default is JSON format, allows user to select between JSON and YAML
        file_path = tkinter.filedialog.asksaveasfilename(defaultextension='.json',
        filetypes=[('JavaScript Object Notation','*.json'),('YAML Ain\'t Markup Language','*.yml')])

        #writes the working archive into the opened file
        with open(file_path,'w') as file:
            yaml.dump(self.archive, file)

if __name__ == '__main__':
    #configures and runs the tkinter backbone
    root = tkinter.Tk()
    root.title('FilmLoggger')
    root.wm_iconbitmap('icon.ico')
    app = FilmLogger(root)
    root.mainloop()
