/*

OnloadScheduler.js

An object allowing tasks to be scheduled to run when the document has loaded

Created by Stephen Morley - http://code.stephenmorley.org/ - and released under
the terms of the CC0 1.0 Universal legal code:

http://creativecommons.org/publicdomain/zero/1.0/legalcode

*/

// create the OnloadScheduler object
var OnloadScheduler =
    new function(){

      // store that the scheduled tasks have not yet been executed
      var executed = false;

      // initialise the lists of tasks
      var negativePriority = [];
      var positivePriority = [];

      /* Executes a set of tasks. The parameter is:
       *
       * tasks - an array of tasks to execute. If this optional parameter is
       *         omitted then all scheduled tasks are executed.
       */
      function execute(tasks){

        // check which tasks should be executed
        if (tasks instanceof Array){

          // execute the tasks
          for (var index = 0; index < tasks.length; index ++){
            try{
              tasks[index]();
            }catch (error){
              // ignore the error
            }
          }

        }else if (!executed){

          // store that the scheduled tasks have been executed
          executed = true;

          // execute the tasks
          for (var index = negativePriority.length - 1; index > 0; index --){
            execute(negativePriority[index]);
          }
          for (var index = 0; index < positivePriority.length; index ++){
            execute(positivePriority[index]);
          }

        }

      }

      /* Schedules a task to be executed. The parameters are:
       *
       * task     - the task to be executed, either as a function or as a string
       * priority - the priority of the task - this optional parameter defaults
       *            to 0
       */
      this.schedule = function(task, priority){

        // set the priority to 0 if it was not supplied
        if (!priority) priority = 0;

        // check whether the task has been supplied as a function
        if (task instanceof Function){

          // store the task in the appropriate list
          if (priority < 0){
            if (!negativePriority[-priority]) negativePriority[-priority] = [];
            negativePriority[-priority].push(task);
          }else{
            if (!positivePriority[priority]) positivePriority[priority] = [];
            positivePriority[priority].push(task);
          }

        }else{

          // schedule a function to execute the code string
          this.schedule(function(){eval(task)}, priority);

        }

      }

      // check which method of adding event listeners is supported
      if ('addEventListener' in document){

        // add a DOMContentLoaded event listener
        document.addEventListener('DOMContentLoaded', execute, false);

        // add a load event listener
        window.addEventListener('load', execute, false);

      }else{

        // check that the doScroll function is supported and this is not a frame
        if ('doScroll' in document.documentElement && window == window.top){

          // repeatedly check whether the page can be scrolled
          (function(){
            try{
              document.documentElement.doScroll('left');
              execute();
            }catch (error){
              window.setTimeout(arguments.callee, 0);
            }
          })();

        }

        // add an onreadystatechange event listener
        document.attachEvent(
            'onreadystatechange',
            function(){
              if (document.readyState == 'complete') execute();
            });

        // add a load event listener
        window.attachEvent('onload', execute);

      }

    }();
