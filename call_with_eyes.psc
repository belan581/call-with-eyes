Funcion action <- read_action (frames)
	// Aquí red neuronal procesando los frames y devolviendo la acción
	// lógica donde evalue los n frames para enviar si 
	// mirar hacia abajo, mirar hacia arriba, cerrar ojos, sin acción
Fin Funcion

Funcion load_video_thread ( start, buffer_array_lenght)
	// buffer por defecto en 20
	Para i<-0 Hasta buffer_array_lenght Con Paso 1 Hacer
		frame <- readCamera
		frame <- mediaPipeDetectLandMarks
		can_process <- can_process_func(frame)
		frames <- pop_frame
		frames <- frame //append
	Fin Para
Fin Funcion

Funcion change_option_thread ( start)
	frames <- [] // variable global
	Mientras !stop_thread Hacer
		Si can_process Entonces
			action <- read_action(frames)
			move_slider(action)
		SiNo
			// No hace nada
		Fin Si
	Fin Mientras
Fin Funcion

Funcion move_slider( action)
	//Funciones para mover slider hacia arriba y abajo
Fin Funcion

Funcion process <- can_process_func( frame)
	// Funcion que detecta si la cabeza está alineada para enviar órdenes
Fin Funcion

Algoritmo call_with_eyes
	// Start Global variables
	stop_thread <- "False"
	can_process <- "False"
	frames <- []
	// Finish global variables
	run_app <- "Run app and load slider"
	load_video_thread(start, buffer_array_lenght=20)
	change_option_thread(start)
FinAlgoritmo
