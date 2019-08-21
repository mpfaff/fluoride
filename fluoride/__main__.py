from fluoride import Level, App

app = App('Fluoride Test')
app.logger.setLevel(Level.FINEST.level)

print('Hello, World!')
app.log(Level.INFO, 'I am Chuck.')
app.log(Level.WARNING, 'There is a chance the world will end soon.')
app.log(Level.FATAL, 'THE WORLD IS ENDING!')
