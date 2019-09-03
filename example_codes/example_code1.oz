functor
import
   Pickle
   System
   Property
   Module
   OS
   Application
   Tk
   Error

define
%declare
   RandomString = 'JcSa0krKRHvcxUupGlWW_'
   Load = Pickle.load
   Save = Pickle.save
   Print = System.print
   Show = System.show
   ShowInfo = System.showInfo
   Apply = Module.apply
   Link = Module.link

   Browse = Show
   Browser = browser(browse:Browse)

   % Prevent warnings if these are not used
   {ForAll [
      RandomString      
      Pickle System Property Module OS Application Tk Load Save Print Show
      ShowInfo Apply Link Browse Browser
    ] Wait}

   %{Property.put 'testcwd' './'}

   try
      {ShowInfo RandomString#start}
      local
         RandomString = unit
         Application = unit
         Error = unit
         Tk = unit
         Module = f(link:Link)
         % Prevent warnings if these are not used
         {ForAll [ RandomString Application Error Tk Module ] Wait}
      in
          \insert 'code.oz'
      end
      {ShowInfo RandomString#stop}
   catch E then
      {ShowInfo RandomString#error}
      {Error.printException E}
      {ShowInfo RandomString#errorEnd}
   finally
      {Tk.send destroy('.')} % Hack against ozwich
      {Application.exit 0}   % Not needed, but it looks clean
   end

end

%====INFORMATION====%
% LFSAB1402 Projet 2016
% Nomas : 06521500-18831500
% Noms : (Blondiaux,Florence)-(Buchet,Delphine)
%====MODULELINK====%
declare
{Property.put 'MyDir' '/home/blondiaux/Documents/Unif/2016-2017/Q3/Info/'}
[Projet]={Module.link ["/home/blondiaux/Documents/Unif/2016-2017/Q3/Info/Projet2016.ozf"]}




%====CODE====%
local % local 1

   MaxTime = 10 % nombre de frame a  l'animation
   MyFunction
   Map
   CheckMap
   Extensions = opt(withExtendedFormula:true
		    withIfThenElse:true
		    withComparison:true
		    withTimeWindow:false
		    withCheckMapEasy:true
		    withCheckMapComplete:true
		   )
in % local 1

   Map = map(ru:[scale(rx:20.0 ry:40.0 1:[primitive(kind:water)])
		 translate(dx: 60.0 dy:80.0 1:[scale(rx: 15.0 ry:50.0 1:[primitive(kind:road)
									 translate(dx:5.0 dy:2.0 1:[rotate(angle:0.78 1:[primitive(kind:building)])])])])
		 translate(dx:100.0 dy:100.0 1:[
						rotate(angle:0.78 1:[
								     scale(rx:100.0 ry:100.0 1:[
											       primitive(kind:building)

											      ])
								     scale(rx:50.0 ry:50.0 1:[
											       primitive(kind:water)
											      ])
								    ])

					       ])

		]

	    pu:[
		 translate(dx:plus(mult(10.0 time) 50.0) dy:mult(10.0 time) 1:[
								    primitive(kind:pokemon)
								   ])
		 translate(dx:plus(15.0 time) dy:plus(16.0 time) 1:[
								    primitive(kind:arena)
								   ])
		 translate(dx:250.0 dy:mult(30.0 time) 1:[
							  primitive(kind:pokestop)
							 ])
		])

%%%%%%%%%%%%%%%%%%%%%%%%%% Begin of MyFunction %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
   fun {MyFunction Map}

%Let's start by define some functions that we will use in the MyFunction

      local %local 2

%-----------------------------Flatten----------------------------------------
   % This function takes a list with sub-lists in it and returns a list without list inside
	 fun {Flatten List}
	    case List of nil then nil
	    []nil|T then {Flatten T}
	    [](H1|H2)|T then {Flatten H1|H2|T}
	    []H|T then H|{Flatten T}
	    else List
	    end % end of case List
	 end % end of fun {Flatten List}

%%%%%%%%%%%%%%%%%%%%%%% Function for Real Universe %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%-----------------------------CheckValue----------------------------------------
%This function checks if X is a value allowed by the program and then computes its value
%It returns a float
%Please note that this function contains the extension "added formulas and values"
/*
 * Validates a chess move.
 *
 * <p>Use {@link #doMove(int theFromFile, int theFromRank, int theToFile, int theToRank)} to move a piece.
 *
 * @param theFromFile file from which a piece is being moved
 * @param theFromRank rank from which a piece is being moved
 * @param theToFile   file to which a piece is being moved
 * @param theToRank   rank to which a piece is being moved
 * @return            true if the move is valid, otherwise false
 * @since             1.0
 */
	 fun {CheckValue X }
	    if {Float.is X} then X
	    else
	       case X of exp( W) then {Float.exp {CheckValue W} }
	       [] log(W) then {Float.log {CheckValue W}}
	       [] neg( W) then ~{CheckValue W }
	       [] plus( W Z)  then {CheckValue W} + {CheckValue Z}
	       [] minus( W Z)  then {CheckValue W}- {CheckValue Z}
	       [] mult(W Z) then {CheckValue W}*{CheckValue Z}
	       [] 'div'(W Z) then {CheckValue W}/{CheckValue Z}
	       [] sin(W) then {Float.sin {CheckValue W}}
	       [] cos(W) then {Float.cos {CheckValue W}}
	       [] tan(W) then {Float.tan {CheckValue W}}
	       [] exp(W) then {Float.exp {CheckValue W}}
	       end % end of case X
	    end % end of if {Float.is}
	 end % end of CheckValue

%------------------------RU-GiveMeThePointWithModification----------------------
%This function returns a point with the modifications include in the List.
	 fun{GiveMeThePointWithModifications List X Y}
	    case List of
	       nil then pt(x:X y:Y)
	    [] H|T then
	       case H of
		  transfo(1:Dx 2:Dy) then {GiveMeThePointWithModifications T {CheckValue plus(X Dx)} {CheckValue plus(Y Dy)}}% For a translate
	       []scale(1:Rx 2:Ry) then {GiveMeThePointWithModifications T {CheckValue mult(X Rx)} {CheckValue mult(Y Ry)}}%For a scale
	       []rot(1:A) then local C D in
				  C= {CheckValue plus(mult(X cos(A)) mult(Y sin(A)))}
				  D = {CheckValue minus(mult(Y cos(A)) mult(X sin(A)))}
				  {GiveMeThePointWithModifications T C D} % For a rotate
			       end%of local  C D
	       end%of case H
	    end%of case List
	 end% of {GiveMeThePointWithModifications List X Y}

%-----------------------------DoRu----------------------------------------------
% This function checks the ru part of the Map, List is the list in ru and ListOfMod
% is an accumulator with all the transformations to do. When we call this function,
% we put ListOfMod at nil
	 fun {DoRu List ListOfMod}
	    case List of nil then nil
	    []H|T then case H of translate(dx:Dx dy:Dy 1:RealList) then
			  {DoRu RealList transfo(1:Dx 2:Dy)|ListOfMod}|{DoRu T ListOfMod}
		       []rotate(angle:A 1:RealList) then
			  {DoRu RealList rot(1:A)|ListOfMod} |{DoRu T ListOfMod}
		       []scale(rx:Rx ry:Ry 1:RealList) then
			  {DoRu RealList scale(1:Rx 2:Ry)|ListOfMod}|{DoRu T ListOfMod}
		       []primitive(kind:RealUniversePOI) then
			  case RealUniversePOI of
			     road then fun {$ Time }
					  realitem(kind:road
						   p1: {GiveMeThePointWithModifications ListOfMod 0.0 0.0}
						   p2: {GiveMeThePointWithModifications ListOfMod 1.0 0.0})
				       end |{DoRu T ListOfMod}
			  else fun {$ Time}
				  realitem(kind:RealUniversePOI
					   p1: {GiveMeThePointWithModifications ListOfMod 0.0 0.0}
					   p2: {GiveMeThePointWithModifications ListOfMod 0.0 1.0}
					   p3: {GiveMeThePointWithModifications ListOfMod 1.0 1.0}
					   p4: {GiveMeThePointWithModifications ListOfMod 1.0 0.0})
			       end  |{DoRu T ListOfMod}
			  end % end of case RealUniversePOI
		       end % end of case H
	    end % end of case List
	 end % end of fun {DoRu List ListOfMod}

%%%%%%%%%%%%%%%%%%%%%%% Function for Poke Universe %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%----------------------------CheckFormula---------------------------------------
% This function checks that X is a formula allows by the program and then computes its value.
% Please note that this function has contains the extensions "added formulas and values",
%"If-then-else" and "comparaison".
	 fun{CheckFormula Time  X}
	    if {Float.is X} then X
	    else
	       case X of
		  time then Time % check
	       [] plus( W Z)  then {CheckFormula Time  W}+ {CheckFormula Time Z} % ok
	       [] minus( W Z)  then {CheckFormula Time  W}- {CheckFormula Time Z} % ok
	       [] mult(W Z) then {CheckFormula Time W}*{CheckFormula Time Z} %ok
	       [] 'div'(W Z) then {CheckFormula Time W}/{CheckFormula Time Z}%ok
	       [] sin(W) then {Float.sin {CheckFormula Time  W}}% ok
	       [] cos(W) then {Float.cos {CheckFormula Time W}}%ok
	       [] tan(W) then {Float.tan {CheckFormula Time W}}
	       [] exp( W) then {Float.exp {CheckFormula Time  W} }
	       [] log( W ) then {Float.log {CheckFormula Time  W}}%ok
	       [] neg( W) then ~{CheckFormula Time  W }
	       [] ite(W Y Z)then if {CheckFormula Time  W} == 0.0 then {CheckFormula Time Z}
				 else {CheckFormula  Time Y}
				 end % end of if in the ite condition
	       [] eq(W Z) then if {CheckFormula  Time  W} == {CheckFormula  Time  Z} then 1.0
			       else 0.0
			       end  % end of if in the eq condition
	       [] ne(W Z) then if  {CheckFormula  Time   W} \= {CheckFormula  Time   Z} then 1.0
			       else 0.0
			       end % end of if in the ne coondition
	       [] lt(W Z) then if {CheckFormula  Time   W} < {CheckFormula  Time   Z} then 1.0
			       else 0.0
			       end %end of if in the lt condition
	       [] le(W Z) then if {CheckFormula  Time   W} =< {CheckFormula  Time   Z} then 1.0
			       else 0.0
			       end % end of if in the le condition
	       [] gt(W Z) then if {CheckFormula  Time   W} > {CheckFormula  Time   Z} then 1.0
			       else 0.0
			       end % end of if in the gt condition
	       [] ge(W Z) then if {CheckFormula  Time   W} >= {CheckFormula  Time   Z} then 1.0
			       else 0.0
			       end % end of if in the ge condition
	       end % end of case X
	    end % end of if {Float.is X} then X
	 end % end of CheckFormula

%----------------------------DoTranslatePu--------------------------------------
%This function applies the translation (Dx Dy) to the elements of List.
	 fun {DoTranslatePu Dx Dy List}
	    case List of nil then nil
	    []H|T then case H of primitive(kind:PokeUniversePOI)  then fun {$ Time}
									  pokeitem(kind:PokeUniversePOI position:pt(x:{CheckFormula Time Dx} y:{CheckFormula Time Dy}))
								       end|{DoTranslatePu Dx Dy T}
		       []translate(dx:X dy:Y 1:PokeUniverse) then {DoTranslatePu plus(X Dx) plus(Y Dy) PokeUniverse} |{DoTranslatePu Dx Dy T}
		       end % end of case H
	    end % end of case List
	 end % end of fun {DoTranslate Pu Dx Dy List}

%----------------------------DoPu-----------------------------------------------
%This function checks the pu part of Map and List is the list in pu.
	 fun {DoPu List}
	    case List of nil then nil
	    []H|T then case H of primitive(kind:PokeUniversePOI) then fun {$ Time }
									 pokeitem(kind:PokeUniversePOI position:pt(x:0.0 y:0.0))
								      end | {DoPu T}
		       []translate(dx:Dx dy:Dy 1:PokeUniverse) then {DoTranslatePu Dx Dy PokeUniverse} |{DoPu T}
		       end % end of case H
	    end % end of case List
	 end % end of fun {DoPu List}

%-------------------------------------------------------------------------------
% We now have all the functions we need in MyFunction

      in %  local 2
	 {Flatten {DoRu Map.ru nil}|{DoPu Map.pu} }
      end % end of local 2
   end % end of MyFunction

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The next function is CheckMap. This function checks that the Map given to MyFunction
% is correct.
% Please note that this function contains the extensions "function to check if
%a map is valide(without extension)" and "function to check if a map is valide
%(with extension)"
% All the following functions returns true or false
   fun{CheckMap Map}
      local % local 3

%%%%%%%%%%%%%%%%%%%%%%%%%%% For RealUniverse %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%---------------------CheckPrimitive-RU-----------------------------------------
% This function checks that the primitive gives in argument is a primitive allowed
% here (kind: building or road or water).
	 fun {CheckPrimitiveRu primitive(kind: RealUniversePOI) }
	    case RealUniversePOI of building then true
	    []water  then true
	    []road then true
	    else false
	    end % end of case RealUniversePOI
	 end % end of fun {CheckPrimitiveRu primitive(kind: RealUniversePOI) }

%-----------------------CheckIfValue-Ru-----------------------------------------
% This function checks that the value X is a value allowed here
	 fun {CheckIfValue X}
	    if {Float.is X} then true
	    else
	       case X of exp( W) then {CheckIfValue W}
	       [] log(W) then {CheckIfValue W}
	       [] neg( W) then {CheckIfValue W }
	       [] plus( W Z)  then {CheckIfValue W} andthen  {CheckIfValue Z}
	       [] minus( W Z)  then {CheckIfValue W} andthen {CheckIfValue Z}
	       [] mult(W Z) then {CheckIfValue W} andthen {CheckIfValue Z}
	       [] 'div'(W Z) then {CheckIfValue W} andthen {CheckIfValue Z}
	       [] sin(W) then {CheckIfValue W}
	       [] cos(W) then {CheckIfValue W}
	       [] tan(W) then {CheckIfValue W}
	       [] exp(W) then {CheckIfValue W}
	       else false
	       end % end of case X
	    end % end of if {Float.is}
	 end % end of fun {CheckIfValue X}

%---------------------------CheckTranslate-RU-----------------------------------
% This function  checks if the translate given in argument is a translate allowed
% here (translate(dx:<value> dy:<value> 1:<RealUniverse>))
	 fun {CheckTranslateRu translate(dx:X dy:Y 1:RealUniverse)}
	    if {CheckIfValue X} andthen {CheckIfValue Y} then
	       {CheckRealUniverse RealUniverse}
	    else false
	    end % end of if {CheckIfValue}
	 end % end of fun {CheckTranslateRu translate(dx:X dy:Y 1:RealUniverse)}

%-----------------CheckRotate-Ru------------------------------------------------
% This function  checks if the rotate given in argument is a rotate allowed
% here (rotate(angle:X 1:<RealUniverse>))
	 fun {CheckRotate rotate(angle: X 1:RealUniverse)}
	    if {CheckIfValue X} then {CheckRealUniverse RealUniverse}
	    else false
	    end % end of if {CheckIfValue X}
	 end % end of fun {CheckRotate rotate(angle: X 1:RealUniverse)}

%-------------------------CheckScale-Ru-----------------------------------------
% This function  checks if the scale given in argument is a scale allowed
% here (scale(rx:<value> ry:<value> 1:<RealUniverse>))
	 fun {CheckScale scale(rx:X ry:Y 1:RealUniverse)}
	    if {CheckIfValue X} andthen {CheckIfValue Y} then
	       {CheckRealUniverse RealUniverse}
	    else false
	    end % end of if {CheckIfValue}
	 end % end of fun {CheckScale scale(rx:X ry:Y 1:RealUniverse)}

%------------------------------CheckRealUniverse-Ru-----------------------------
% This function  checks if RealUniverse given in argument is a RealUniverse allowed
% here

	 fun {CheckRealUniverse RealUniverse}
	    case RealUniverse of nil then true
	    [] H|T then case H of primitive(kind: RealUniversePOI) then if {CheckPrimitiveRu primitive(kind: RealUniversePOI) }
									then {CheckRealUniverse T}
									else false
									end % end of if {CheckPrimitive primitive(kind: RealUniversePOI) }
			[] translate(dx:X dy:Y 1:RealUniverse)  then if {CheckTranslateRu translate(dx:X dy:Y 1:RealUniverse)}
								     then {CheckRealUniverse T}
								     else false
								     end % end of if {CheckTranslate translate(dx:X dy:Y 1:RealUniverse)}
			[] rotate(angle:X 1:RealUniverse) then if {CheckRotate rotate(angle: X 1:RealUniverse)}
							       then {CheckRealUniverse T}
							       else false
							       end % end of if {CheckRotate rotate(angle: X 1:RealUniverse)}
			[] scale(rx:X ry:Y 1:RealUniverse) then if {CheckScale scale(rx:X ry:Y 1:RealUniverse)}
								then {CheckRealUniverse T}
								else false
								end % end of if {CheckScale scale(rx:X ry:Y 1:RealUniverse)}
			else false
			end % end of case H
	    else false
	    end % end of case RealUniverse
	 end % end of fun {CheckRealUniverse RealUniverse}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%% FOR PokeUniverse %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%---------------------------CheckPrimitive-PU-----------------------------------
% This function checks if the primitive given in argument is a primitive allowed here
% (primitive(kind:pokemon or arena or pokestop))
	 fun {CheckPrimitivePu primitive(kind: PokeUniversePOI) }
	    case PokeUniversePOI of pokemon then true
	    []arena  then true
	    []pokestop then true
	    else false
	    end % end of case PokeUniversePOI
	 end % end of fun {CheckPrimitivePu primitive(kind: PokeUniversePOI) }

%---------------------------CheckIfFormula-PU----------------------------------
% This function checks if the formula given in argument is a formula allowed here
	 fun {CheckIfFormula X}
	    if {Float.is X} then true
	    else
	       case X of
		  time then true
	       [] plus( W Z)  then {CheckIfFormula W} andthen  {CheckIfFormula Z}
	       [] minus( W Z)  then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] mult(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] 'div'(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] sin(W) then {CheckIfFormula W}
	       [] cos(W) then {CheckIfFormula W}
	       [] tan(W) then {CheckIfFormula W}
	       [] exp( W) then {CheckIfFormula W}
	       [] log( W ) then {CheckIfFormula W}
	       [] neg( W) then {CheckIfFormula W}
	       [] ite(W Y Z)then {CheckIfFormula W} andthen {CheckIfFormula Z} andthen {CheckIfFormula Y}
	       [] eq(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] ne(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] lt(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] le(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] gt(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       [] ge(W Z) then {CheckIfFormula W} andthen {CheckIfFormula Z}
	       else false
	       end % end of case X
	    end % end of if {Float.is X}
	 end % end of fun {CheckIfFormula X}

%---------------------------CheckTranslate-PU-----------------------------------
% This function checks if the translate given in argument is a translate allowed here
	 fun {CheckTranslatePu translate(dx:X dy:Y 1:PokeUniverse)}
	    if {CheckIfFormula X} andthen {CheckIfFormula Y} then
	       {CheckPokeUniverse PokeUniverse}
	    else false
	    end % end of if {CheckIfFormula}
	 end % end of fun {CheckTranslatePu translate(dx:X dy:Y 1:PokeUniverse)}

%---------------------------CheckPokeUniverse-PU--------------------------------
% This function checks if the PokeUniverse given in argument is a PokeUniverse
% allowed here
	 fun { /* this is a test Haha */ CheckPokeUniverse PokeUniverse}
	    case PokeUniverse of nil then true
	    []H|T then case H of primitive(kind: PokeUniversePOI) then if {CheckPrimitivePu primitive(kind: PokeUniversePOI) }
								       then {CheckPokeUniverse T}
								       else false
								       end % end of if {CheckPrimitivePu }
		       [] translate(dx:X dy:Y 1:RealUniverse) then if  {CheckTranslatePu translate(dx:X dy:Y 1:RealUniverse)}
								   then {CheckPokeUniverse T}
								   else false
								   end % enf of if {CheckTranslatePu }
		       else false
		       end % end of case H
	    else false
	    end % end of case PokeUniverse
	 end % end of fun {CheckPokeUniverse PokeUniverse}

%---------------------- start of CheckMap --------------------------------------
% We have now define all the functions we need in CheckMap
% @pre some infos @post some more infos
      in % of local 3
	 case Map of nil then false
	 [] map(ru:RealUniverse pu:PokeUniverse) then if {CheckRealUniverse RealUniverse}
						      then {CheckPokeUniverse PokeUniverse}
						      else false
						      end % end of {CheckRealUniverse}
	 else false
	 end % end of case Map
      end % end local 3
   end % end of fun  CheckMap
%------------------------------end of CheckMap ---------------------------------

%   {Browse {CheckMap Map}}
   {Projet.run MyFunction Map MaxTime Extensions CheckMap}

end % end of local 1

