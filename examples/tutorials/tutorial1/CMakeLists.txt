add_test(NAME tutorial1_step0 COMMAND bash -c "source $KESSEL_ROOT/share/kessel/setup-env.sh; kessel reset; kessel run" WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/0)
add_test(NAME tutorial1_step1 COMMAND bash -c "source $KESSEL_ROOT/share/kessel/setup-env.sh; kessel reset; kessel run" WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/1)
add_test(NAME tutorial1_step2 COMMAND bash -c "source $KESSEL_ROOT/share/kessel/setup-env.sh; kessel reset; kessel run" WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/2)
add_test(NAME tutorial1_step3 COMMAND bash -c "source $KESSEL_ROOT/share/kessel/setup-env.sh; kessel reset; kessel run" WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/3)
