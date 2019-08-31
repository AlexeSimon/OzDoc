local
 
   [Project] = {Link ['Project2018.ozf']}
   Time = {Link ['x-oz://boot/Time']}.1.getReferenceTime

            % Fonction transformant une note ou un silence en une extended note ou un extended silence
            % IN : <note> ou <silence> 
            % Out : <extended note> dont les champs ont ete mis a jour
            fun {NoteToExtended Note}
                case Note
                of Name#Octave then 
                    note(name:Name octave:Octave sharp:true duration:1.0 instrument:none)
		        [] note(name:N octave:O sharp:S duration:D instrument:I) then
		            Note
                [] silence(duration:D) then
            		  Note
                [] Atom then
                    case {AtomToString Atom}
                    of [_] then
                        note(name:Atom octave:4 sharp:false duration:1.0 instrument:none)
                    [] [N O] then
                        note(name:{StringToAtom [N]}
                             octave:{StringToInt [O]}
                             sharp:false
                             duration:1.0
            	             instrument: none) 
            	    else
            	        silence(duration:1.0)
            	    end
                end
            end

%-----------------------------------------------------------------------------
%                             PARTIE 1 - PartitionToTimedList
%-----------------------------------------------------------------------------
    fun {PartitionToTimedList Partition}
    
        local


            % 1. Stretch
            
            % Fonction etirant la duree de chaque note ou accord par le facteur indique
            % IN: <float> Factor , <partition> Partition sans transformation
            % OUT: <partition> dont la duree a ete multipliee par Factor
            fun {Stretch Factor Partition}
                local
                
                    % Sous-Fonction de Stretch
                    % IN: <float> Factor, <extended note> ExtNote 
                    % OUT: <extended note> dont la duree a ete multipliee par Factor
                    fun {StretchNote Factor ExtNote}
                        local NewNote 
                        in
                            case ExtNote 
                            of note(name:N octave:O sharp:S duration:D instrument:I) then
                    	       NewNote = note(name:N octave:O sharp:S duration:D*Factor instrument:I)
                            [] silence(duration:D) then
                    	        NewNote = silence(duration:D*Factor)
                	        else
                    	        NewNote = nil
                    	    end
                	        NewNote
                        end
                    end
                in
                
                    case Partition
                    of H|T then 
                        case H                      % H est un partition item
                        of H2|T2 then               % Cas ou la partition contient un accord
                            ({Stretch Factor H2}|{Stretch Factor T2})|{Stretch Factor T}
                        else                        % Cas ou H represente une note ou d'un silence
                            local NewNote in
                                NewNote = {NoteToExtended H}
                                {StretchNote Factor NewNote}|{Stretch Factor T}
                            end
                        end
                    else
                        if Partition==nil then
                            nil
                        else
                            local NewNote in
                                NewNote = {NoteToExtended Partition}
                                {StretchNote Factor NewNote}
                            end
                        end
                    end
                end
            end
             
    
            % 2. Duration
    
            % Fonction fixant la duree de la partition par le temps specifie
            % IN: <float> Seconds, <partition> Partition sans transformation
            % OUT: <partition> dont la duree a ete modifiee
            fun{Duration Seconds Partition}
               local Factor CounterTime in
                    fun{CounterTime Partition A}
                        case Partition
                        of H|T then
                            case H
                            of H2|T2 then
                               {CounterTime T A+{CounterTime H2 0.0}}
                            else
                               local NewNote in
                                    NewNote={NoteToExtended H}
                                    {CounterTime T A+NewNote.duration}
                               end
                            end
                        [] nil then
                            A
                        else % partition constituee d'une note
                            {CounterTime Partition A}
                        end
                    end
                    Factor = Seconds/{CounterTime Partition 0.0} % division flottante
                    {Stretch Factor Partition}
               end
            end
       
            %3. Drone
        
            % Fonction repetant la note ou l'accord K fois
            % IN: <note> ou <chord> X, <integer> K
            % OUT: Liste de notes ou d'accords repetes
            fun {Drone X K}
                local NewNote RepeatNote Convert in
                    fun{RepeatNote N K}
                        if K>0 then
                            N|{RepeatNote N K-1}
                        else
                            nil
                        end
                    end
                
                    fun{Convert Chord}
                        case Chord 
                        of H|T then
                            {NoteToExtended H}| {Convert T}
                        else
                            nil
                        end
                    end
                    
                    case X 
                    of H|T then 
                        NewNote = {Convert X}
                    else
                        NewNote = {NoteToExtended X}  
                    end
                    
                    {RepeatNote NewNote K}
                end
            end
            
            %4. Transpose 
            
            % Fonction transposant la partition d'un certain nombre de demi-tons vers le haut ou  vers le bas
            % IN: <integer> , <partition> sans transformations
            % OUT: Partition transposee de quelques demi-tons
            fun {Transpose K Partition}
                local Gamme IndexNote TransposeNote in
                    Gamme = gamme(0:note(name:c sharp:false) 1:note(name:c sharp:true) 
                            2:note(name:d sharp:false) 3:note(name:d sharp:true) 
                            4:note(name:e sharp:false) 5:note(name:f sharp:false) 
                            6:note(name:f sharp:true) 7:note(name:g sharp:false) 
                            8:note(name:g sharp:true) 9:note(name:a sharp:false) 
                            10:note(name:a sharp:true) 11:note(name:b sharp:false))
        
                    % Fonction qui retourne l'indice d'une note dans l'enregistrement <gamme>
                    % IN: <extended note> Note
                    % OUT: <integer> represantant l'indice de la note correspondante dans l'enregistrement
                    fun{IndexNote Note}
                        case Note
                        of note(name:N octave:O sharp:S duration:D instrument:I) then 
                            local 
                                fun{LookUp R N Count}
                                    if (R.Count).name == N then 
                                        Count
                                    else
                                        {LookUp R N Count+1}
                                    end
                                end
                            in
                                {LookUp Gamme Note.name 0}
                            end
                        else 
                            ~1
                        end
                    end
		   
                    % Fonction transposant une note d'un certain nombre de demi-tons vers le haut ou ver les bas
                    % IN : <integer>, <ExtendedNote> 
                    % OUT: Note transposee
                    fun {TransposeNote K ExN}
                        local SumIndex Octaf NewIndex NewNote in
                            case ExN
                            of silence(duration:D) then
                                ExN
                            else
                                SumIndex= K+ {IndexNote ExN}
                                Octaf = SumIndex div 12 
                                % Les douzes notes existent pour chaque octave, en divisant par douze, 
                                % on determine ainsi quelle est la nouvelle octave de la nouvelle note transposee.
                                NewIndex = SumIndex mod 12 
                                % En calculant le reste de la division de <SumIndex> par douze, 
                                % on determine sur quelle nouvelle note nous nous retrouvons
			        NewNote = note(name:((Gamme.NewIndex).name) octave:(ExN.octave+Octaf) sharp:((Gamme.NewIndex).sharp) duration:ExN.duration
					      instrument:ExN.instrument)
                                NewNote
                            end
                        end
                    end
        
                    case Partition
                    of nil then nil
                    [] H|T then % partition formee d'une liste d'elements
                        case H
                        of H2|T2 then % Cas ou la partition contient un accord 
                            ({Transpose K H2} | {Transpose K T2})|{Transpose K T}
                        else
                            local NewNote in
                                NewNote = {NoteToExtended H} 
                                {TransposeNote K NewNote}|{Transpose K T}
                            end
                        end
                     else
                	   local NewNote in
                	      NewNote={NoteToExtended Partition}
                	      {TransposeNote K NewNote}
                	   end
                    end
                end
            end
            
            
            % TRANSFO
            % Fonction executant toutes les transformations contenues dans une partition
            % IN: <partition> Partition
            % OUT: <flat partition> 
            fun {Transfo Partition}
                case Partition 
                of H|T then 
                    case H 
                    of duration(seconds:S 1:Part2) then 
                        {Duration S  {Transfo Part2}} | {Transfo T}
                    [] stretch(factor:F 1:Part2) then
                        {Stretch F {Transfo Part2}} | {Transfo T}
                    [] drone(note:N amount:A) then
                        {Drone N A} | {Transfo T}
                    [] transpose(semitones:S 1:Part2) then
                        {Transpose S {Transfo Part2}} | {Transfo T}
                    [] H2|T2 then 
                        ({NoteToExtended H2} | {Transfo T2}) | {Transfo T}
        		    else
        		       {NoteToExtended H}|{Transfo T}
                    end
                else
                    nil
                end
            end

	    
	       
        in
        
            local MaPartition in
            
	       MaPartition = {Transfo Partition} % Execute toutes les transformations de la partition introduite
	                                         % comme argument de la fonction <PartitionToTimedList>
               MaPartition
            end
            
	end
	   
    end


%-----------------------------------------------------------------------------
%                             PARTIE 2 - MIX
%-----------------------------------------------------------------------------
    
    % Fonction interpretant l'argument Music pour retourner une liste d'echantillons
    % IN: <function> satisfaisant la specification de la fonction PartitionToTimedList, <music> 
    % OUT: <list> de <sample> 
    fun {Mix P2T Music}
        local 
        
            % Fonction calculant la hauteur d'une note
            % IN : <extendedNote> 
            % OUT : <integer> nombre de demi-tons entre cette note et A4 
            fun{Height Note}
                local Gamme IndexNote IndexRef OctaveRef Index Octave NbreOctave Hauteur in
                   Gamme = gamme( 0:note(name:a sharp:false) 1:note(name:a sharp:true) 2:note(name:b sharp:false)
                                  3:note(name:c sharp:false) 4:note(name:c sharp:true) 5:note(name:d sharp:false)
                    		      6:note(name:d sharp:true) 7:note(name:e sharp:false) 8:note(name:f sharp:false)
                    		      9:note(name:f sharp:true) 10:note(name:g sharp:false) 11:note(name:g sharp:true) )
                    		     
                    %Fonction qui retourne l'indice d'une note dans le record gamme
                    % IN: <extended note>
                    % OUT: <integer> l'indice dans l'enregistrement
                    fun{IndexNote ExN}
                        case ExN
                        of note(name:N octave:O sharp:S duration:D instrument:I) then 
                            local 
                                fun{LookUp R N Count}
                                    if (R.Count).name == N then 
                                        Count
                                    else
                                        {LookUp R N Count+1}
                                    end
                                end
                            in
                                {LookUp Gamme ExN.name 0}
                            end
                        else 
                            ~1
                        end
                    end   
                   
                    IndexRef = 0                % Correspondant au A4 
                	OctaveRef = 4
                	Index = {IndexNote Note}
                	Octave = Note.octave	
                	NbreOctave = Octave - OctaveRef
                    Hauteur = NbreOctave *12  + Index
                    Hauteur
                end
            end
            
            
            % Fonction transformant une note en un echantillon code a 44100[Hz]
            % IN: <exentedNote>
            % OUT: <liste> de sample compris dans l'intervalle [-1;1]
            fun{NoteToSample Note}
                local
                    Pi = 3.14159265359
                    Hauteur = {Int.toFloat {Height Note}}
                    Frequence = {Number.pow 2.0 Hauteur/12.0} * 440.0
                    Duree =  Note.duration
                    NbreEchantillons =  Duree * 44100.0 + 1.0                       
                    
                    fun{ToList A}
                            if  A < NbreEchantillons then 
            		            (1.0/2.0) * {Float.sin (2.0*Pi*Frequence* A)/44100.0} | {ToList A+1.0}
                            else
                                nil
                            end
            	    end
                in
                   {ToList 1.0}
                end
            end
            
            % Fonction transformant un silence en un echantillon code a 44100[Hz]
            % IN: <silence> ou  <extended silence>
            % OUT: Sample compris dans l'intervalle [-1;1]
            fun{SilenceToSample S}
                local Duree in
                    case S
                    of silence(duration:D) then
                        Duree = D
                    else
                        Duree = 1.0
                    end
                    
                    local
                        NbreEchantillons =  Duree * 44100.0 + 1.0
                        fun{ToList A}
                                if  A < NbreEchantillons then 
                		            0.0 | {ToList A+1.0}
                                else
                                    nil
                                end
                	    end
                    in
                       {ToList 1.0}
                    end
                end
            end
            
            % Fonction transformant un accord en un sample en faisant la moyenne des signaux des notes
            %       jouees simultanement
            % IN : <extended chord>
            % OUT : <sample> compris dans l'intervalle [-1;1]
            fun {ChordToSample Accord}
                
                local Pi AllFrequencies NumberOfNotes AllSinus in
                
                    Pi = 3.14159265359
                    
                    % Fonction enregistrant dans une liste 
                    %   chaque frequence associees aux notes de l'accord
                    % IN : <extended chord>
                    % OUT: <liste> contenant les frequences associees aux notes de l'accord
                    fun{AllFrequencies Accord}
                        case Accord
                        of H|T then
                            {Number.pow 2.0 {Int.toFloat {Height H}}/12.0} * 440.0 | {AllFrequencies T}
                        else
                            nil
                        end
                    end
                    
                    % Fonction calculant le nombre de notes dans un accord
                    % IN: <chord> 
                    % OUT: <natural> nombre de notes dans l'accord
                    fun{NumberOfNotes Accord Acc}
                        case Accord
                        of H|T then 
                            {NumberOfNotes T Acc+1}
                        else
                            Acc
                        end
                    end
                
                
                    % Fonction creant une liste avec tous les sinus des differentes notes de l'accord
                    % IN: <list> des frequences des notes 
                    % OUT: liste des sinus dans la formule Ai 
                    fun {AllSinus Liste}
                        local NbreNotes Duree NbreEchantillons Expression Create
                        in
                            NbreNotes = {NumberOfNotes Liste 0}
                            Duree = (Accord.1).duration
                            NbreEchantillons = Duree *  44100.0 
                            
                            % Fonction calculant le signal emis par une note en particulier a un temps I
                            % IN: <natual> I 
                            % OUT: Signal emis par une note au temps i
                            fun{Expression I Liste}
                                case Liste
                                of H|T then
                                    (1.0/2.0) * {Float.sin (2.0*Pi*H*I)/44100.0} + {Expression I T} 
                                else
                                    0.0
                                end
                            end
                            
                            % Fonction qui repete la formule a tous les i 
                            % IN: <integer> accumulateur 
                            % OUT: <liste>
                            fun{Create Acc}
                                if Acc<NbreEchantillons then
                                    ({Expression Acc Liste}/{Int.toFloat NbreNotes}) | {Create Acc+1.0}
                                else 
                                    nil
                                end
                            end    
                            {Create 0.0}
                        end
                    end
                    {AllSinus {AllFrequencies Accord}}
                end       
            end
                
                
                
            % Fonction convertissant une partition en une liste d'echantillons
            % IN : <flat partition>
            % OUT : <samples>
            fun{PartitionToSamples Partition}
                case Partition
                of H|T then
                    case H
                    of note(name:N octave:O sharp:S duration:D instrument:I) then
                        {Append {NoteToSample H} {PartitionToSamples T}}
                    [] H2 | T2 then %cas ou il s'agit d'un accord
                        {Append {ChordToSample H} {PartitionToSamples T}}
                    [] silence(duration:D) then % cas ou il s'agit d'un silence
                        {Append {SilenceToSample H} {PartitionToSamples T}}
                    [] silence then
                        {Append {SilenceToSample H} {PartitionToSamples T}}
                    else
                        nil
                    end
                else
                    nil
                end
            end
            
            % Fonction transformant une <part> en <sample>
            % IN: <part>
            % OUT: <samples>
            fun{ToSample Part}
                case Part 
                of samples(1:S) then
                    S
                [] partition(1:P) then
                    {PartitionToSamples {P2T P}} 
                [] wave(1:FileName) then
                    {Project.readFile FileName}
                [] merge(1:MusicWithIntensities) then
                    {Merge MusicWithIntensities}
                    
                else %si c'est un filtre
                    case Part 
                    of reverse(1:Music) then
                        {Reverse {MusicToSample Music}}
                    [] repeat(amount:K 1:Music) then
                        {Repeat K {MusicToSample Music}}
                    [] loop(seconds:S 1:Music) then
                        {Loop S {MusicToSample Music}}
                    [] clip(low:S high:J 1:Music) then
                        {Clip S J {MusicToSample Music}}
                    [] echo(delay:D decay:Factor 1:Music) then
                        {Echo D Factor {MusicToSample Music}}
                    [] fade(start:S out:D 1:Music) then
                        {Fade S D {MusicToSample Music}}
                    [] cut(start:D finish:F 1:Music) then
                        {Cut D F {MusicToSample Music}}
                    else
                        nil
                    end
                end
            end
            
            
            fun{MusicToSample Music}
                case Music
                of H|T then
                    {Append {ToSample H} {MusicToSample T}}
                else
                    nil
                end
            end
            
            % Merge 
            
            % Fonction supersosant plusieurs musiques
            % IN: <music with intensities>
            % OUT: <music>
            fun{Merge MusicWI}
                
                local 
                    
                    % Fonction multipliant toutes les samples d'une musique par son facteur associe 
                    % IN: <Music with intensities>
                    % OUT: Liste de Sample
                    fun{Multiplying M}
                        case M
                        of H|T then     %pattern matching de la music with intenities 
                            case H      % H est une music
                            of Factor#Music then
                                local SampleListe in
                                    SampleListe = {MusicToSample Music} 
                                    local
                                        fun{Multiply Fact List}
                                            case List 
                                            of H2|T2 then
                                                H2*Fact|{Multiply Fact T2}
                                            else
                                                nil
                                            end
                                        end
                                    in
                                        {Multiply Factor SampleListe}|{Multiplying T}
                                    end
                                end
                            else
                                nil
                            end 
                        else
                            nil
                        end
                    end
                    
            % A ce stade, la music a ete convertie en sample dont les valeurs ont ete multipliees par les facteurs associes
            
                    
                    %IN: <list> sortant de Multpiplying 
                    fun{Summing ListOfL}
                        local LengthMax LMax LonList SumL IndexL GetIndex in
                            %Retourne la longueur d'une liste
                            fun{LonList L A}
                                case L
                                of H|T then
                                    {LonList T A+1}
                                else
                                    A
                                end
                            end
                            
                            % Fonction List.nth 
                            fun{GetIndex L N}
                                case L
                                of H|T then
                                    if N>1 then 
                                        {GetIndex T N-1}
                                    else
                                        H
                                    end
                                else
                                    nil
                                end
                            end
                            
                            % Fonction qui retourne l'index de la liste la plus longue de la liste en argument
                            % IN: <list>, longueur, index, accumulateurdont chaque element est une liste
                            % OUT: <integer> 
                            fun{LengthMax Liste Long Index Acc}
                                case Liste
                                of H|T then % Liste est une liste de liste donc H est a nouveau une liste
                                    local Longueur in
                                        Longueur = {LonList H 0}
                                        if (Longueur > Long) then
                                            {LengthMax T Longueur Acc Acc+1}
                                        else
                                            {LengthMax T Long Index Acc+1}
                                        end
                                    end
                                else
                                    Long
                                end
                            end
                            LMax = {LengthMax ListOfL 1 1 1}
                            fun{SumL List Acc}
                                if Acc =< LMax then
                                    local 
                                        % Additione le nieme element de chaque liste dans L
                                        fun{AddNthElem L N A}
                                            case L
                                            of H|T then
                                                if {LonList H 0} < N then
                                                    {AddNthElem T N A} %Si la liste est plus courte on comble avec des silences
                                                else
                                                    {AddNthElem T N A+{GetIndex H N}}
                                                end
                                            else
                                                A
                                            end
                                        end
                                    in 
                                        {AddNthElem List Acc 0.0}|{SumL List Acc+1}
                                    end
                                else
                                    nil
                                end
                            end
                            {SumL ListOfL 1}
                        end
                    end
                in
                    {Summing {Multiplying MusicWI}}
                end
            end
                        

            
        % Tous les <filter>
        
        %1. Reverse
            % Inverse la liste d'echantillons
            % IN: <music>
            % OUT: <music> dont la liste d'echantillons a ete inversee
            fun{Reverse Music}
                local
                    fun {DoReverse Xs Ys}
                        case Xs
                        of X|Xr then
                            {DoReverse Xr X|Ys}
                        else
                            Ys
                        end
                    end
                in
                    {DoReverse Music nil}
                end
            end
            
            % 2. Repeat
            % Fonction repetant une musique un certain nombre de fois
            % IN : <natural> K , Music
            % OUT : <Music> repetee K fois
            fun {Repeat K Music}
                local
                    fun{RepeatSample N K2}
                        if K2>0 then
                            {Append N {RepeatSample N K2-1}}
                        else
                            nil
                        end
                    end
                in
                    case Music 
                    of H|T then
            	        {RepeatSample Music K}
                    else
                        nil
                    end
                end
            end
            
            % 3. Loop : Joue la musique en boucle durant une certaine duree.
            % IN: <duration>, <music>
            % OUT: <music>
            fun{Loop Time Music}
                local 
                    % Savoir combien d'echantillons il y a dans musique pour avoir la duree de celle ci
                    fun{CountSample Music A}
                        case Music
                        of H|T then
                            {CountSample T A+1.0}
                        else
                            A
                        end
            	    end
            	                       
            	    % La fonction est appelee apres avoir copie un nmbr entier de fois la musique
                	fun{EndingLoop Music Tref}
                        if Tref > 0.0 andthen Music \= nil then
                            Music.1|{EndingLoop Music.2 (Tref-1.0)}
                        else
                            nil
                        end
                	end
                	
                	fun{AmountOfRepeat N T Acc}
                        if (T-N)>0.0 then
                            {AmountOfRepeat N T-N Acc+1.0}
                        else
                            Acc
                        end
                	end
                in
                    local NbrEchant Amount Tref in
                    
                        NbrEchant = {CountSample Music 0.0}
                        Amount = {AmountOfRepeat NbrEchant Time*44100.0 0.0}
                        
                        Tref = Time*44100.0 - NbrEchant*Amount
                        {Append {Repeat {Float.toInt Amount} Music} {EndingLoop Music Tref}}
                        
                    end
                end
            end


        
            % 4. Clip
            % Fonction bornes les samples et remplace les depassants par la borne
            % IN: <foat> low entre -1 et 1, <float> high entre -1 et 1, <Sample>
            % OUT: <sample> dont les valeurs sont comprises entre <low> et <high>
            fun{Clip Low High Sample}
                case Sample
                of H|T then
                    if H > High orelse H < Low then
                        if H > High then
                            High|{Clip Low High T}
                        else
                            Low|{Clip Low High T}
                        end
                    end
                else 
                    nil
                end
            end

            % 5. Echo
            % Fonction superposant deux listes identiques mais decalees dans le temps de delay multipliee d'un facteur decay
            % IN: <duration>, <factor>, <music>
            % OUT: <music> avec superposition de la meme music decalee pour l'echo
            fun{Echo Delay Decay Music}
                local MusicDecalee NbrEchantillonsRetard Collage MusicWithIntensities DelayList in
                    NbrEchantillonsRetard = Delay * 44100.0
                    
                    % Fonction qui ajoute N 0 devant la liste = Colle les zeros avant la musique
                    % IN: <list> liste a laquelle on souhaite ajouter des zeros devant, <float> N nombre de zeros a ajouter
                    % OUT: <list> precedee de N* 0
                    fun{Collage L N}
                        if N>0.0 then
                            0.0|{Collage L N-1.0}
                        else
                            L
                        end
                    end
                    
                    DelayList = {Collage Music NbrEchantillonsRetard}
                    MusicWithIntensities= 1.0#Music | Decay#DelayList | nil
                    
                    {Merge MusicWithIntensities}
                end
            end
            
        
        
% 6. Fade
            % Fonction adoussisant les transitions 
            % IN: <integer> nombre de secondes , <integer> nombre de secondes, <sample>
            % OUT: <sample> 
            fun{Fade Start Stop Sample}
            
                local NbreDebut PasDebut FactorIncreasing Augmentation NbreFin PasFin FactorDecreasing Diminution NbrEchantillon PremierAModifier Main in
                    NbreDebut = Start * 44100.0 % Nombre d'echantillons a modifier pour le debut
                    PasDebut = 1.0/NbreDebut                   % Calcul du pas
                    
                    % Fonction renvoyant une liste avec les facteurs d'intensites croissants
                    % IN: <Integer> Acc = 0.0
                    % OUT: <list> avec les facteurs croissants
                    fun{FactorIncreasing Acc}
                        if (Acc =< 1.0) then
                            Acc|{FactorIncreasing Acc+PasDebut}
                        else
                            nil
                        end
                    end
                    
                    Augmentation = {FactorIncreasing 0.0}
                    
                    NbreFin = Stop * 44100.0 % Nombre d'echantillon a modifier pour la fin
                    PasFin = 1.0/NbreFin                     % Calcul du pas
                    
                    % Fonction renvoyant une liste avec les facteurs d'intensites decroissants
                    % IN: <Integer> Acc = 1.0
                    % OUT: <list> avec les facteurs decroissants
                    fun{FactorDecreasing Acc}
                        if Acc >= 0.0 then
                            Acc|{FactorDecreasing Acc-PasFin}
                        else
                            nil
                        end
                    end
                    
                    Diminution = {FactorDecreasing 1.0}
                    
                    fun{NbrEchantillon Sample Acc}
                        case Sample 
                        of H|T then
                            {NbrEchantillon T Acc+1.0}
                        else
                            Acc
                        end
                    end
                    
                    PremierAModifier = {NbrEchantillon Sample 0.0} - NbreFin -1.0
                    
                    % Sous-fonction principale 
                    % - augmentant lineairement l'intervalle d'echantillon [0;Start] 
                    % - laissant intacte la partie centrale
                    % - diminuant lineairement l'intervalle d'echantillon [PremierAModifier; NbreEchantillons] 
                    % IN: <Increasing> = liste croissants des facteurs, <sample> = Sample original, <Decreasing> = liste decroissante des facteurs 
                    % OUT: sample avec les premiers echantillons d'intensites croissantes et les derniers d'intensites decroissantes
                    
                    fun {Main Increasing Sample Decreasing Acc}
                        case Sample
                        of H|T then %patern maching sur Liste
                            case Increasing     %patern maching sur Increasing
                            of H1|T1 then
                                H*H1| {Main T1 T Decreasing Acc+1.0}
                            else                % cas ou tous la liste des intensites croissante est entierement parcourue
                                if Acc < PremierAModifier then              % partie de la liste a laisser intacte
                                    H|{Main Increasing T Decreasing Acc+1.0}
                                else
                                    case Decreasing 
                                    of H2|T2 then
                                        H2*H|{Main Increasing T T2 Acc+1.0} %NB: changer l'accumulateur ici n'apporte rien mais pour la coherence il a tout de meme ete incremente
                                    else
                                        nil
                                    end
                                end
                            end
                        else
                            nil
                        end
                    end
                    {Main Augmentation Sample Diminution 0.0}
                end
            end


%7.     
            % Fonction selectionnant une partie de la musique situee entre Start et Stop
            % IN: Start Finish Music
            % OUT: Sample
            fun{Cut Start Finish Music}
            
                local Sample TropCourt NbreSilenceAAjouter DureeTotale EchantillonDepart EchantillonFin NbrSamples NbrSamples NbreEchantillons Main in
                    Sample = {MusicToSample Music}
                    
                    EchantillonDepart = Start * 44100.0        % Echantillon de depart
                    EchantillonFin = Finish * 44100.0          % Echantillon de fin
                    
                    fun{NbrSamples Sample Acc}
                        case Sample 
                        of H|T then
                            {NbrSamples T Acc+1.0}
                        else
                            Acc
                        end
                    end
                    NbreEchantillons = {NbrSamples Sample 0.0}
                    
                    DureeTotale = NbreEchantillons * 44100.0
                    
                    if EchantillonFin > NbreEchantillons then % cas ou l'intervalle depasse la taille de la musique
                        TropCourt = true                % La musique est en effet trop courte et doit etre completees par des silences
                    else
                        TropCourt = false
                    end
                
                    fun{Main Sample Acc AccSilence}
                        case Sample
                        of H|T then
                            if Acc < EchantillonDepart then       % Cas ou il ne faut pas recuperer la fonction
                                {Main T Acc+1 AccSilence}
                            elseif TropCourt == false andthen Acc >= EchantillonDepart andthen Acc =< EchantillonFin then % Cas ou il faut copier les valeur
                                H|{Main T Acc+1 AccSilence} 
                            else 
                                nil
                            end
                            
                        else % cas ou on est arrive au bout de tous les echantillons
                            
                            NbreSilenceAAjouter = DureeTotale * 44100.0 - Acc
                            if AccSilence < NbreSilenceAAjouter then  % cas ou on est arrive a la fin du Sample et ou il faut ajouter des silences
                                0.0|{Main Sample Acc AccSilence+1.0}
                            else
                                nil 
                            end
                        end
                    end
                    {Main Sample 0.0 0.0}
                end
            end
            
        in
            {MusicToSample Music}
        end
    end

   Music = {Project.load 'example.dj.oz'}
   Start
   
in

   Start = {Time}
   
   % Instruction pour eviter l'erreur "local variable used only once"
   {ForAll [NoteToExtended Music Start] Wait}
   
   % Calls your code, prints the result and outputs the result to `out.wav`.
   {Browse {Project.run Mix PartitionToTimedList Music 'out.wav'}}
   
   % Affiche le temps total pris pour executer le code
   {Browse {IntToFloat {Time}-Start} / 1000.0}
end