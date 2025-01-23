<?php
/*
======================= API NAMING CONVETION =======================
The goals of the naming convention are to have a short, descriptive, and predictable name
for each function that will sort related functions near one another alphabetically
- Camel Case
- Lower Case First letter
- No Spaces
- Noun First
- Verb Last
- Use a underscore between the item and the verb
EX: gameInstance_get, gameInstance_create, gameInstance_edit, gameInstance_copy
Available Verbs:
- get   	(retrive a value)
- create	(create/save a new value)
- delete	(remove a value)
- edit  	(update a value)
- copy  	(duplicate a value)
- do    	(action when the above verbs dont fit)
- Other verbs can be used, but only when the above do not fit
*/

namespace Materia;
use \Materia\Msg;
use \Materia\Util_Validator;

class Api_V1
{
	/**
	 * Finds widgets that are specified in the database as spotlight widgets.
	 */
	static public function widgets_get($widgets = null)
	{
		return Widget_Manager::get_widgets($widgets);
	}

	/**
	 * Finds widgets based on a given preset criteria ("all", etc)
	 */
	static public function widgets_get_by_type($type)
	{
		return Widget_Manager::get_widgets([], $type);
	}

	static public function widget_instances_get($inst_ids = null, bool $deleted = false)
	{
		// get all my instances - must be logged in
		if (empty($inst_ids))
		{
			if (\Service_User::verify_session() !== true) return Msg::no_login(); // shortcut to returning noting
			return Widget_Instance_Manager::get_all_for_user(\Model_User::find_current_id());
		}

		// get specific instances - no log in required
		if ( ! is_array($inst_ids)) $inst_ids = [$inst_ids]; // convert string into array of items
		return Widget_Instance_Manager::get_all($inst_ids, false, false, $deleted);
	}

/**
 * Takes a page number, and returns objects containing the total_num_pages and
 * widget instances that are visible to the user.
 *
 * @param page_number The page to be requested. By default it is set to 1.
 *
 * @return array of objects containing total_num_pages and widget instances that are visible to the user.
 */
	static public function widget_paginate_user_instances_get($page_number = 0)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		$data = Widget_Instance_Manager::get_paginated_instances_for_user(\Model_User::find_current_id(), $page_number);
		return $data;
	}

	/**
	 * @return bool, true if successfully deleted widget instance, false otherwise.
	 */
	static public function widget_instance_delete($inst_id)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! static::has_perms_to_inst($inst_id, [Perm::FULL]) && ! Perm_Manager::is_support_user()) return Msg::no_perm();
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;

		$result = $inst->db_remove();
		if ($result)
		{
			return $inst_id;
		}
		else
		{
			return Msg::failure('Failed to remove widget instance from database');
		}
	}

	static public function widget_instance_access_perms_verify($inst_id)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();

		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);

		if ( ! static::has_perms_to_inst($inst_id, [Perm::VISIBLE, Perm::FULL]))
		{
			return Msg::no_perm();
		}
		return true;
	}

	/**
	 * @return object, contains properties indicating whether the current
	 * user can edit the widget and a message object describing why, if not
	 */

	 // !! this endpoint should be significantly refactored or removed in the future API overhaul !!
	static public function widget_instance_edit_perms_verify(string $inst_id)
	{
		$response = new \stdClass();

		$response->is_locked = false;
		$response->can_publish = false;
		$response->can_edit = false;

		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		else if (\Service_User::verify_session() !== true) return Msg::no_login();
		else if ( ! ($inst = Widget_Instance_Manager::get($inst_id)))  throw new \HttpNotFoundException;

		$response->is_locked = ! Widget_Instance_Manager::locked_by_current_user($inst_id);
		$response->can_publish = $inst->widget->publishable_by(\Model_User::find_current_id());
		$response->can_edit = static::has_perms_to_inst($inst_id, [Perm::FULL]);

		return $response;
	}

	/**
	 * @return bool, true if the current user can publish the given widget instance, false otherwise.
	 */
	static public function widget_publish_perms_verify(int $widget_id)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! Util_Validator::is_pos_int($widget_id)) return Msg::invalid_input($widget_id);

		$widget = new Widget();
		if ( $widget->get($widget_id) == false) return Msg::invalid_input('Invalid widget type');

		return $widget->publishable_by(\Model_User::find_current_id());
	}

	static private function has_perms_to_inst($inst_id, $perms)
	{
		return Perm_Manager::user_has_any_perm_to(\Model_User::find_current_id(), $inst_id, Perm::INSTANCE, $perms);
	}

	// copies a widget instance
	static public function widget_instance_copy(string $inst_id, string $new_name, bool $copy_existing_perms = false)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! static::has_perms_to_inst($inst_id, [Perm::FULL]) && ! Perm_Manager::is_support_user()) return Msg::no_perm();
		$inst = Widget_Instance_Manager::get($inst_id, true);
		if ( ! $inst) return Msg::failure('Widget instance could not be found.');

		try
		{
			// retain access - if true, grant access to the copy to all original owners
			$current_user_id = \Model_User::find_current_id();
			if ( ! $current_user_id) return Msg::failure('Could not find current user.');
			$duplicate = $inst->duplicate($current_user_id, $new_name, $copy_existing_perms);
			return $duplicate;
		}
		catch (\Exception $e)
		{
			return Msg::failure('Widget instance could not be copied.');
		}
	}

	/**
	 * @param int     $widget_id The Game resource ID
	 * @param object  $qset
	 * @param bool    $is_draft Whether the widget is being saved as a draft
	 * @param int     $inst_id (optional) The id of the game (widget) we're saving
	 *
	 * @return array An associative array with details about the save
	 */

	static public function widget_instance_save($widget_id=null, $name=null, $qset=null, $is_draft=null)
	{
		return static::widget_instance_new($widget_id, $name, $qset, $is_draft);
	}

	static public function widget_instance_new($widget_id=null, $name=null, $qset=null, $is_draft=null)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if (\Service_User::verify_session('no_author')) return Msg::invalid_input('You are not able to create or edit widgets.');
		if ( ! Util_Validator::is_pos_int($widget_id)) return Msg::invalid_input($widget_id);
		if ( ! is_bool($is_draft)) $is_draft = true;

		$widget = new Widget();
		if ( $widget->get($widget_id) == false) return Msg::invalid_input('Invalid widget type');
		if ( ! $is_draft && ! $widget->publishable_by(\Model_User::find_current_id()) ) return Msg::no_perm('Widget type can not be published by students.');
		if ( $is_draft && ! $widget->is_editable) return Msg::failure('Non-editable widgets can not be saved as drafts!');

		$is_student = ! \Service_User::verify_session(['basic_author', 'super_user']);
		$inst = new Widget_Instance([
			'user_id'         => \Model_User::find_current_id(),
			'name'            => $name,
			'is_draft'        => $is_draft,
			'created_at'      => time(),
			'widget'          => $widget,
			'is_student_made' => $is_student,
			'guest_access'    => $is_student,
			'attempts'        => -1
		]);

		if ( ! empty($qset->data)) $inst->qset->data = $qset->data;
		if ( ! empty($qset->version)) $inst->qset->version = $qset->version;

		try
		{
			$inst->db_store();
			return $inst;
		}
		catch (\Exception $e)
		{
			trace($e);
			return Msg::failure('Widget instance could not be saved.');
		}
	}

	/**
	 * Save and existing instance
	 *
	 * @param int     $inst_id
	 * @param string  $name
	 * @param object  $qset
	 * @param bool    $is_draft Whether the widget is being saved as a draft
	 * @param int     $open_at
	 * @param int     $close_at
	 * @param int     $attempts
	 * @param bool    $guest_access
	 * @param bool 	  $is_student_made // NOT USED
	 *
	 * @return array An associative array with details about the save
	 */
	static public function widget_instance_update($inst_id=null, $name=null, $qset=null, $is_draft=null, $open_at=null, $close_at=null, $attempts=null, $guest_access=null, $embedded_only=null, $is_student_made=null)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if (\Service_User::verify_session('no_author')) return Msg::invalid_input('You are not able to create or edit widgets.');
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input('Instance id is invalid');
		if ( ! static::has_perms_to_inst($inst_id, [Perm::FULL])) return Msg::no_perm();

		$inst = Widget_Instance_Manager::get($inst_id, true);
		if ( ! $inst) return Msg::failure('Widget instance could not be found.');
		if ( $is_draft && ! $inst->widget->is_editable) return Msg::failure('Non-editable widgets can not be saved as drafts!');
		if ( ! $is_draft && ! $inst->widget->publishable_by(\Model_User::find_current_id())) return Msg::no_perm('Widget type can not be published by students.');

		// student made widgets are locked forever
		if ($inst->is_student_made)
		{
			if ($guest_access === false)
			{
				return new Msg('Student-made widgets must stay in guest access mode.', 'Student Made', 'error', false);
			}
			$attempts = -1;
			$guest_access = true;
		}

		if ( ! empty($qset->data) && ! empty($qset->version))
		{
			$inst->qset = $qset;
		}
		else
		{
			// if the qset is not explicitly provided, assume it is not being updated
			// if $inst->qset is populated it will be saved to the db as a new qset version - which isn't necessary
			$inst->qset = (object) ['version' => null, 'data' => null];
		}
		if ( ! empty($name))
		{
			if ($inst->name != $name)
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Name',
					'value_2' => $name
				]);
				$activity->db_store();
			}
			$inst->name = $name;
		}
		if ($is_draft !== null)
		{
			if ($inst->is_draft != $is_draft)
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Is Draft',
					'value_2' => $is_draft
				]);
				$activity->db_store();
			}
			$inst->is_draft = $is_draft;
		}
		if ($open_at !== null)
		{
			if ($inst->open_at != $open_at)
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Open At',
					'value_2' => $open_at
				]);
				$activity->db_store();
			}
			$inst->open_at = $open_at;
		}
		if ($close_at !== null)
		{
			if ($inst->close_at != $close_at)
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Close At',
					'value_2' => $close_at
				]);
				$activity->db_store();
			}
			$inst->close_at = $close_at;
		}
		if ($attempts !== null)
		{
			if ($inst->attempts != $attempts)
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Attempts',
					'value_2' => $attempts
				]);
				$activity->db_store();
			}
			$inst->attempts = $attempts;
		}
		if ($guest_access !== null)
		{
			// if the user is a student and they're not the owner, they can't do anything
			// if the user is a student and they're the owner, they're allowed to set it to guest access
			if (($inst->user_id == \Model_User::find_current_id() && $guest_access) || ! Perm_Manager::is_student(\Model_User::find_current_id()))
			{
				if ($inst->guest_access != $guest_access)
				{
					$activity = new Session_Activity([
						'user_id' => \Model_User::find_current_id(),
						'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
						'item_id' => $inst_id,
						'value_1' => 'Guest Access',
						'value_2' => $guest_access
					]);
					$activity->db_store();
				}
				$inst->guest_access = $guest_access;
				// when disabling guest mode on a widget, make sure no students have access to that widget
				if ( ! $guest_access)
				{
					$access = Perm_Manager::get_all_users_explicit_perms($inst_id, Perm::INSTANCE)['widget_user_perms'];
					foreach ($access as $user_id => $user_perms)
					{
						if (Perm_Manager::is_student($user_id) && $user_id != $inst->user_id)
						{
							\Model_Notification::send_item_notification(\Model_user::find_current_id(), $user_id, Perm::INSTANCE, $inst_id, 'disabled', null);
							Perm_Manager::clear_user_object_perms($inst_id, Perm::INSTANCE, $user_id);
						}
					}
				}
			}
		}

		if ($embedded_only !== null)
		{
			// if current user is student, they cannot change embedded_only
			if ($inst->embedded_only != $embedded_only && ! Perm_Manager::is_student(\Model_User::find_current_id()))
			{
				$activity = new Session_Activity([
					'user_id' => \Model_User::find_current_id(),
					'type'    => Session_Activity::TYPE_EDIT_WIDGET_SETTINGS,
					'item_id' => $inst_id,
					'value_1' => 'Embedded Only',
					'value_2' => $embedded_only
				]);
				$activity->db_store();

				$inst->embedded_only = $embedded_only;
			}
		}

		try
		{
			$inst->db_store();
			return $inst;
		}
		catch (\Exception $e)
		{
			return Msg::failure('Widget could not be created.');
		}
	}

	/**
	 * Lock a widget to prevent others from editing it
	 * @return true if we have or are able to get a lock on this game
	 */
	static public function widget_instance_lock($inst_id)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! static::has_perms_to_inst($inst_id, [Perm::VISIBLE, Perm::FULL])) return Msg::no_perm();
		return Widget_Instance_Manager::lock($inst_id);
	}

	static public function session_play_create($inst_id, $context_id=false)
	{
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();
		if ( $inst->is_draft == true) return Msg::failure('Drafts Not Playable', 'Must use Preview to play a draft.');

		$play = new Session_Play();
		$play_id = $play->start(\Model_User::find_current_id(), $inst_id, $context_id);
		return $play_id;
	}

	static public function session_logout()
	{
		$activity = new Session_Activity([
			'user_id' => \Model_User::find_current_id(),
			'type'    => Session_Activity::TYPE_LOGGED_OUT
		]);
		$activity->db_store();
		return \Auth::logout();
	}

	static public function session_login($user, $pass)
	{
		return \Service_User::login($user, $pass);
	}

	/**
	 * Dedicated session validation call for the creator. Because a play isn't created, no need to verify session user w/ model user.
	  */
	static public function session_author_verify($role_name = null)
	{
		return \Service_User::verify_session($role_name);
	}

	/**
	 * Session validation call for the player. Performs the standard session verification and additionally verifies that the user currently authenticated matches the user stored in play data.
	 */
	static public function session_play_verify($play_id)
	{
		// Standard session validation first
		if (\Service_User::verify_session() !== true) return Msg::no_login();

		// if $play_id is null, assume it's a preview, no need for user check
		if ( ! $play_id) return true;

		// Grab user id from play data
		$play_data = new Session_Play();
		$play_data->get_by_id($play_id);

		// Grab id of currently authenticated user
		$current_user_id = \Model_User::find_current_id();

		// Compare and return boolean
		return $play_data->user_id == $current_user_id;
	}

	/**
	 * Get play activity history based on user's user_id
	 */
	static public function play_activity_get($start = 0, $range = 6)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		// get play data, ask for one more than was requested so we can see if there are more
		// we grabbed an extra entry, just to see if there are more than requested
		// but we don't want to include that in the results
		$play  = new Session_Play();
		$plays = $play->get_plays_by_user_id(\Model_User::find_current_id(), $start, $range + 1);
		$count = count($plays);
		if ($count > $range) $plays = array_slice($plays, 0, $range);
		return [
			'activity' => $plays,
			'more'     => $count > $range
		];
	}

	static public function play_logs_save($play_id, $logs, $preview_inst_id = null)
	{
		if ( ! $preview_inst_id)
		{
			$inst = self::_get_instance_for_play_id($play_id);
			if ( ! $inst->playable_by_current_user()) return Msg::no_login();

			// Ensure user comparison between session & model checks out
			if ( ! $inst->guest_access && self::session_play_verify($play_id) !== true) return Msg::no_login();
		}
		else
		{
			// No user in session, just perform auth check
			if (\Service_User::verify_session() !== true) return Msg::no_login();
		}

		if ( $preview_inst_id === null && ! Util_Validator::is_valid_long_hash($play_id)) return Msg::invalid_input($play_id);
		if ( ! is_array($logs) || count($logs) < 1 ) return Msg::invalid_input('missing log array');

		// ============ PREVIEW MODE =============
		if (Util_Validator::is_valid_hash($preview_inst_id))
		{
			Score_Manager::save_preview_logs($preview_inst_id, $logs);
			return true;
		}
		// ============ PLAY FOR KEEPS ===========
		else
		{
			$play = self::_validate_play_id($play_id);
			if ( ! ($play instanceof Session_Play)) return Msg::invalid_input('Invalid play session');
			// each log is an object?, convert to array
			if ( ! is_array($logs[0]))
			{
				$len = count($logs);
				for ($i = 0; $i < $len; $i++)
				{
					$logs[$i] = (array)($logs[$i]);
				}
			}

			Session_Logger::parse_and_store_log_array($play_id, $logs);

			// we may not have loaded the widget yet
			if ( ! isset($inst->widget))
			{
				$inst = Widget_Instance_Manager::get($play->$inst_id);
			}

			$class = $inst->widget->get_score_module_class();
			$score_mod = new $class($play->id, $inst, $play);
			$score_mod->log_problems = true;

			// make sure that the logs arent timestamped wrong or recieved incorrectly
			if ($score_mod->validate_times() == false)
			{
				$play->invalidate();
				return Msg::failure('Timing validation error.');
			}

			// if widget is not scorable, check for a participation score log
			// if one is found, use it as a "score" event for LTI passback
			if ( ! $inst->widget->is_scorable)
			{
				foreach ($logs as $log)
				{
					if (Session_Logger::get_type($log['type']) == Session_Log::TYPE_SCORE_PARTICIPATION)
					{
						\Event::trigger('score_updated', [$play->id, $play->inst_id, $play->user_id, $log['value'], 100], 'string');
					}
				}
			}

			// validate the scores the game generated on the server
			try
			{
				$score_mod->validate_scores();
			}
			catch (Score_Exception $e)
			{
				$play->invalidate();
				return Msg::failure($e->message, $e->title);
			}

			$return = [];

			if ($score_mod->finished == true)
			{
				$play->set_complete($score_mod->verified_score, $score_mod->total_questions, $score_mod->calculated_percent);

				$event_returns = \Event::trigger('play_completed', $play, 'array');

				foreach ($event_returns as $event_return_arr)
				{
					$return = array_merge($return, $event_return_arr);
				}
			}

			$return['score'] = $score_mod->calculated_percent;

			return $return;
		}
	}

	static public function assets_get()
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		return Widget_Asset_Manager::get_assets_by_user(\Model_User::find_current_id(), Perm::FULL);
	}

	/**
	 * Returns all scores for the given widget instance recorded by the current user, and attmepts remaining in the current context.
	 * If no launch token is supplied, the current semester will be used as the current context.
	 *
	 * @param string $inst_id The widget instance ID
	 * @param string $token The launch token corresponding to the first play in a series of replays, if it exists
	 *
	 * @return array An array containing a list of scores as an array and the number of attempts left in the current context, if applicable
	 */
	static public function widget_instance_scores_get($inst_id, $token=false)
	{
		$result = $token ? \Event::trigger('before_score_display', $token) : null;
		$context_id = empty($result) ? null : $result;
		if ( ! $token && \Session::get('context_id', false)) $context_id = \Session::get('context_id');

		$semester = Semester::get_current_semester();

		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		$scores = Score_Manager::get_instance_score_history($inst_id, $context_id);
		$attempts_used = count(Score_Manager::get_instance_score_history($inst_id, $context_id, $semester));
		$extra = Score_Manager::get_instance_extra_attempts($inst_id, \Model_User::find_current_id(), $context_id, $semester);

		$attempts_left = $inst->attempts - $attempts_used + $extra;

		return [
			'scores' => $scores,
			'attempts_left' => $attempts_left
		];
	}

	static public function widget_instance_play_scores_get($play_id, $preview_mode_inst_id = null)
	{
		// if not preview, see if current user can play widget
		if ( ! $preview_mode_inst_id)
		{
			$inst = self::_get_instance_for_play_id($play_id);
			if ( ! $inst->playable_by_current_user()) return Msg::no_login();
		}
		// otherwise see if user has valid session
		else
		{
			if (\Service_User::verify_session() !== true) return Msg::no_login();
		}

		if (Util_Validator::is_valid_hash($preview_mode_inst_id))
		{
			$inst = Widget_Instance_Manager::get($preview_mode_inst_id);
			$preview_logs = Score_Manager::get_preview_logs($inst);
			if ( ! is_array($preview_logs)) return Msg::expired();
			else return $preview_logs;
		}
		else
		{
			if (Util_Validator::is_valid_long_hash($play_id) != true) return Msg::invalid_input($play_id);
			return Score_Manager::get_play_details([$play_id]);
		}
	}

	/**
	 * Gets a single score corresponding to a play_id for guest widgets.
	 *
	 * @param int $inst_id The widget instance ID
	 * @param int $play_id The play ID
	 *
	 * @return array Single item array which holds the score or is empty
	 */
	static public function guest_widget_instance_scores_get($inst_id, $play_id)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();
		return Score_Manager::get_guest_instance_score_history($inst_id, $play_id);
	}

	/**
	 *	Gets scores/players for a particular game
	 *	Returns an array with the following:
	 *
	 *	@return array [players]     a list of players that played this game <br />
	 *				  [quickStats]	contains attempts, scores, currentPlayers, avScore, replays <br />
	 *				  [playLogs]    a log of all scores recoreded
	 */
	static public function play_logs_get($inst_id, $semester = 'all', $year = 'all', $page_number=1)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! static::has_perms_to_inst($inst_id, [Perm::VISIBLE, Perm::FULL])) return Msg::no_perm();
		$is_student = ! \Service_User::verify_session(['basic_author', 'super_user']);

		$data = Session_Play::get_by_inst_id_paginated($inst_id, $semester, $year, $page_number, $is_student);
		return $data;
	}

	/**
	 * Gets score distributions (total and by semester) for a widget instance.
	 * See documentation in Score_Manager for more information.
	 */
	static public function score_summary_get($inst_id, $include_storage_data = false)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		$distribution = Score_Manager::get_widget_score_distribution($inst_id);
		$summary = Score_Manager::get_widget_score_summary($inst_id);

		foreach ($distribution as $id => $data)
		{
			if ( ! array_key_exists($id, $summary))
			{
				$summary[$id] = $data;
			}
			else
			{
				$summary[$id]['distribution'] = $data['distribution'];
			}
		}

		if ($include_storage_data)
		{
			$storage = Storage_Manager::get_table_summaries_by_inst_id($inst_id);
			foreach ($storage as $id => $data)
			{
				if ( ! array_key_exists($id, $summary))
				{
					$summary[$id] = $data;
					$summary[$id]['storage'] = $summary[$id]['data'];
					unset($summary[$id]['data']);
				}
				else
				{
					$summary[$id]['storage'] = $data['data'];
				}
			}
		}

		$summary = array_values($summary);
		// we want to be sure that the client can rely on the array order
		usort($summary, function($a, $b) {
			return($b['id'] - $a['id']);
		});
		return $summary;
	}

	/**
	 * Gets an unsorted array containing all completed scores for a widget for the current semester, unless requested otherwise
	 *
	 * @param int $inst_id The widget instance ID
	 * @param bool $get_all Flag to request all scores for a widget, not just those of the current semester
	 *
	 * @return array Flat array that holds numerical scores for the widget for the requested time frame
	 */
	static public function score_raw_distribution_get($inst_id, $get_all = false)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		// ask the score module if it allows score_distribution
		try{
			$class = $inst->widget->get_score_module_class();
			$score_mod = new $class(-1, $inst);
			if ( ! $score_mod || empty($score_mod->allow_distribution) ) return false;
		}
		catch (\Exception $e) {
			trace("Error loading score module for {$inst_id}");
			return Msg::failure("Error loading score module for {$inst_id}");
		}

		$result = null;

		if ($get_all == true)
		{
			$result = Score_Manager::get_all_widget_scores($inst_id);
		}
		else
		{
			$semester = Semester::get_current_semester();
			$result = Score_Manager::get_widget_scores_for_semester($inst_id, $semester);
		}

		$scores = [];
		foreach ($result as $score)
		{
			$scores[] = (int) $score['score'];
		}
		return $scores;
	}

	/**
	 * Gets Storage Data (if any) for the widget with the given instance ID.
	 * Current user must have access permission to the widget.
	 * @param int $inst_id the The id of the widget instance to request
	 * @return array Array containing storage data for this widget instance
	 */
	static public function play_storage_get($inst_id)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		return Storage_Manager::get_storage_data($inst_id);
	}
	/**
	 * Gets the Question Set for the widget with the given instance ID.
	 * Current user must have author/collab access to the widget or
	 * a valid play ID for this to work.
	 * @notes users that are logged in and already have a valid play ID have already passed access test, so no need to try again
	 * @param int $inst_id The id of the widget instance to get the qset for (formerly inst_id)
	 * @param int $play_id The play id associated with a play session
	 * @param int $timestamp The timestamp after which no qsets should be returned
	 * @return object QSET
	 */
	static public function question_set_get($inst_id, $play_id = null, $timestamp = false)
	{
		if ( ! Util_Validator::is_valid_hash($inst_id) ) return Msg::invalid_input($inst_id);
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		// valid play id sent?
		if ( ! empty($play_id) && ! $timestamp && ! static::_validate_play_id($play_id))
		{
			return Msg::no_login();
		}

		// if preview mode, can I preview?
		if (empty($play_id) && ! $inst->viewable_by(\Model_User::find_current_id())) return Msg::no_perm();

		$inst->get_qset($inst_id, $timestamp);

		return $inst->qset;
	}

	/**
	 * Generates a question set based on a given instance ID, widget ID, topic, and whether to include images.
	 * @param string $inst_id The instance ID, if there is an instance associated with this request. May be null.
	 * @param string $widget_id The ID of the widget engine associated with this request. Must be set.
	 * @param string $topic The topic for which to generate a question set
	 * @param bool $include_images whether or not to include images in the generated qset
	 * @param int $num_questions How many questions should be generated in the qset
	 * @param bool $build_off_existing Whether to build from an existing qset, or generate one from scratch
	 * @return object The generated question set
	 */
	static public function question_set_generate($inst_id, $widget_id, $topic, $include_images, $num_questions, $build_off_existing)
	{
		// short-circuit if generation is not available
		if ( ! Widget_Question_Generator::is_enabled()) return Msg::failure();

		// verify eligibility
		if ( ! \Service_User::verify_session(['basic_author', 'super_user'])) return Msg::no_perm();

		$inst = null;

		// validate instance (but only if an instance id is provided)
		if (Util_Validator::is_valid_hash($inst_id))
		{
			if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
			if ( ! $inst->playable_by_current_user()) return Msg::no_login();
		}

		$widget = new Widget();
		if ( $widget->get($widget_id) == false) return Msg::invalid_input('Invalid widget type');
		if ( ! $widget->is_generable) return Msg::invalid_input('Widget engine does not support generation');

		// clean topic of any special characters
		$topic = preg_replace('/[^a-zA-Z0-9\s]/', '', $topic);

		// validate number of questions
		if ($num_questions < 1) $num_questions = 8;
		if ($num_questions > 32) $num_questions = 32;

		$query = Widget_Question_Generator::generate_qset($inst, $widget, $topic, $include_images, $num_questions, $build_off_existing);
		if ( ! $query instanceof Msg && is_array($query))
		{
			return [
				...$query,
				'title' => $topic
			];
		}
		else
		{
			\Log::error(print_r($query, true));
			return $query;
		}
	}

	/**
	 * Endpoint to facilitate AI text generation for widgets
	 *
	 * @param string $prompt The prompt to generate.
	 * @return array An array to be passed back to the widget containing the response string
	 */
	static public function widget_prompt_generate($prompt)
	{
		// verify eligibility
		if ( ! Widget_Question_Generator::is_enabled()) return Msg::failure();
		if (\Service_User::verify_session() !== true) return Msg::no_login();

		// prompt generation & response handling
		$result = Widget_Question_Generator::generate_from_prompt($prompt);
		if ( ! $result instanceof Msg && is_string($result))
		{
			return [
				'success'  => true,
				'response' => $result
			];
		}
		else
		{
			\Log::error(print_r($result, true));
			return $result;
		}
	}

	/**
	 * Gets the question with the given QID or an array of questions
	 * with the given ids (passed as an array)
	 *
	 * @param int|array $ids The Question ID or IDs of the questions to get.
	 *
	 * @return array|object An array of questions requested or a question requested
	 */
	static public function questions_get($ids=null, $type=null) // remote_getQuestions
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		// get specific questions
		if ($ids)
		{
			if ( ! is_array($ids)) return Msg::invalid_input($ids);
			$questions = [];
			foreach ($ids as $id)
			{
				if ($question = Widget_Question::forge()->db_get($id))
				{
					$questions[] = $question;
				}
			}
			return $questions;
		}
		// get all my questions
		else
		{
			return Widget_Question_Manager::get_users_questions(\Model_User::find_current_id(), $type);
		}
	}

	static public function play_storage_data_save($play_id, $data)
	{
		$inst = self::_get_instance_for_play_id($play_id);
		if ( ! $inst->playable_by_current_user()) return Msg::no_login();

		// Make sure widget is being played by the correct user (when guest access not enabled)
		if ( ! $inst->guest_access && self::session_play_verify($play_id) !== true) return Msg::no_login();

		if ($play = Api_V1::_validate_play_id($play_id)) //valid play id or logged in
		{
			$user_id = $inst->guest_access ? 0 : $play->user_id; // store as guest or user?
			Storage_Manager::parse_and_store_storage_array($play->inst_id, $play_id, $user_id, $data);
			return true;
		}
		else
		{
			return Msg::no_login();
		}
	}

	static public function play_storage_data_get($inst_id, $format=null) // formerly $inst_id
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! Util_Validator::is_valid_hash($inst_id)) return Msg::invalid_input($inst_id);
		switch ($format)
		{
			case 'csv':
				return Storage_Manager::get_csv_logs_by_inst_id($inst_id);

			default:
				return Storage_Manager::get_storage_data($inst_id);
		}
	}

	static public function semester_date_ranges_get()
	{
		return Utils::get_date_ranges();
	}

	/**
	 * Paginated search for users that match input
	 *
	 * @param string Search query
	 * @param string Page number
	 * @return array List of users
	 */
	static public function users_search($input, $page_number = 0)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();

		$items_per_page = 50;
		$offset = $items_per_page * $page_number;

		// query DB for only a single page + 1 item
		$displayable_items = \Model_User::find_by_name_search($input, $offset, $items_per_page + 1);

		$has_next_page = sizeof($displayable_items) > $items_per_page ? true : false;

		if ($has_next_page) array_pop($displayable_items);

		foreach ($displayable_items as $key => $person)
		{
			$displayable_items[$key] = $person->to_array();
		}

		$data = [
			'pagination' => $displayable_items,
		];

		if ($has_next_page) $data['next_page'] = $page_number + 1;

		return $data;
	}
	/**
	 * Gets information about the current user
	 *
	 * @return object   User object
	 * @return bool     False if error or no login
	 */
	static public function user_get($user_ids = null)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		$results = [];

		//no user ids provided, return current user
		if ($user_ids === null)
		{
			//$results = \Model_User::find_current();
			$me = \Model_User::find_current_id();
			$results = \Model_User::find($me);
			$results = $results->to_array();
		}
		else
		{
			if (empty($user_ids) || ! is_array($user_ids)) return Msg::invalid_input();
			//user ids provided, get all of the users with the given ids
			$me = \Model_User::find_current_id();

			foreach ($user_ids as $id)
			{
				if (Util_Validator::is_pos_int($id))
				{
					$user = \Model_User::find($id);
					$user = $user->to_array();
					$user['isCurrentUser'] = ($id == $me);
					$results[] = $user;
				}
			}
		}
		return $results;
	}
	/**
	 * Updates the user's meta data
	 *
	 * @return int   User id
	 * @return bool  True if successful, otherwise returns an error
	 */
	static public function user_update_meta($new_meta)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! is_array($new_meta)) return Msg::invalid_input('meta');
		if (empty($new_meta)) return true;

		$user = \Model_User::find_current();
		foreach ($new_meta as $key => $val)
		{
			$user->profile_fields[$key] = $val;
		}
		return $user->save();
	}

	private static function _normalize_perms($perms_array)
	{
		// convert each permission object in the perms array to a integer indexed array of values
		foreach ($perms_array as &$perm_obj)
		{
			// convert perms to an array
			if ( ! is_array($perm_obj->perms)) $perm_obj->perms = (array) $perm_obj->perms;

			// convert the keys from string numeric keys to integers
			foreach ($perm_obj->perms as $key => $value)
			{
				if ( ! is_int($key))
				{
					// convert string numeric keys to number keys
					unset($perm_obj->perms[$key]);
					$perm_obj->perms[(integer) $key] = $value;
				}
			}
		}
		return $perms_array;
	}

	private static function _filter_increasing_perms($perms, $current_perms)
	{
		// I can only reduce my perms, filter out anything that increases or adds
		foreach ($perms->perms as $key => $value)
		{
			// remove any perm I didn't already have
			if ( ! array_key_exists($key, $current_perms))
			{
				unset($perms->perms[$key]);
				continue;
			}
			// make sure i'm not enabling anything i didn't already have
			if ($value != $current_perms[$key] && $value == Perm::ENABLE)
			{
				$perms->perms[$key] = $current_perms[$key];
			}
		}
		return $perms;
	}

	/**
	 * @param array   An array with user_id's and the perms to assign them
	 *				  Example:
	 *				  [0]
	 *             ['user_id'] => 5443
	 *             ['expiration'] => null                 // null expiration == no expiration //
	 *             ['perms'] => [ [0] => 1, [30] => 1]
	 */
	static public function permissions_set($item_type, $item_id, $perms_array)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		if ( ! Util_Validator::is_valid_hash($item_id)) return Msg::invalid_input('Invalid item id: '.$item_id);
		if (empty($perms_array)) return Msg::invalid_input('empty user perms');

		$perms_array = static::_normalize_perms($perms_array);

		$cur_user_id = \Model_user::find_current_id();

		// full perms or is super user required
		$can_give_access = Perm_Manager::user_has_any_perm_to($cur_user_id, $item_id, $item_type, [Perm::FULL]) || \Service_User::verify_session('super_user');

		// if we're changing permissions on a widget instance, have that instance on hand for checking
		$inst = false;
		$refused = [];

		// filter out any permissions I can't do
		foreach ($perms_array as &$new_perms)
		{
			// i cant do anything
			if ( ! $can_give_access && $new_perms->user_id != $cur_user_id) return Msg::no_perm();

			$old_perms = Perm_Manager::get_user_object_perms($item_id, $item_type, $new_perms->user_id);
			$requested_perm_count = count($new_perms->perms);

			// I can only reduce my perms, filter out anything that increases or adds
			if ( ! $can_give_access && $new_perms->user_id == $cur_user_id)
			{
				$new_perms = static::_filter_increasing_perms($new_perms, $old_perms);
			}

			// Toss out an error if all the perms I asked for get filtered out
			if ($requested_perm_count > 0 && count($new_perms->perms) < 1 ) return Msg::no_perm();

			// Determine what type of notification to send
			// Search perms for enabled value and get key (new_perm)
			// array_search returns false if value was not found
			// need strict type checking because 0 == false
			$new_perm   = array_search(Perm::ENABLE, $new_perms->perms);
			$is_enabled = $new_perm !== false;

			// set VIEW access for all of its assets
			if ($item_type === Perm::INSTANCE)
			{
				// get the widget instance if we don't have it yet
				if ( ! $inst) $inst = Widget_Instance_Manager::get($item_id);

				// if we're sharing the instance with a student, make sure it's okay to share with students first
				if ($is_enabled && Perm_Manager::is_student($new_perms->user_id))
				{
					// guest mode isn't enabled - don't give this student access
					if ( ! $inst->allows_guest_players())
					{
						$refused[] = $new_perms->user_id;
						continue;
					}
					Perm_Manager::set_user_game_asset_perms($item_id, $new_perms->user_id, [Perm::VISIBLE => $is_enabled], $new_perms->expiration);
				}
			}

			Perm_Manager::set_user_object_perms($item_id, $item_type, $new_perms->user_id, $new_perms->perms, $new_perms->expiration);
			$notification_mode = '';

			if ( ! $is_enabled)
			{
				$notification_mode = 'disabled';
			}
			elseif ($old_perms != [$new_perm => Perm::ENABLE])
			{
				$notification_mode = 'changed';
			}

			\Model_Notification::send_item_notification($cur_user_id, $new_perms->user_id, $item_type, $item_id, $notification_mode, $new_perm);
		}

		if (count($refused) > 0)
		{
			return Msg::student_collab();
		}

		return true;
	}
	/**
	 * Returns all perms for an item
	 *
	 * @param int the number of the type of item (game, question, asset, etc)
	 * @param int the items id (for a game use the Game Instance ID, etc)
	 *
	 * @return array Contains an array with the uid and the permission number of that user.
	 *
	 * @notes getGameSharingStatus getPendingShares
	 */
	static public function permissions_get($item_type, $item_id)
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();
		return Perm_Manager::get_all_users_explicit_perms($item_id, $item_type);
	}

	static public function notifications_get()
	{
		if (\Service_User::verify_session() !== true) return Msg::no_login();

		$notifications = \Model_Notification::query()
			->where('to_id', \Model_User::find_current_id())
			->get();

		$return_array = [];

		foreach ($notifications as $notification)
		{
			$return_array[] = $notification->to_array();
		}

		//API conversion process requires an array, not JSON formatted data
		return $return_array;
	}

	static public function notification_delete($note_id, $delete_all)
	{
		if ( ! \Service_User::verify_session()) return Msg::no_login();

		$user = \Model_User::find_current();

		if ($delete_all)
		{
			$notes = \Model_Notification::query()
				->where('to_id', $user->id)
				->get();

			foreach ($notes as $note)
			{
				$note->delete();
			}
			return true;
		}
		if ($note_id)
		{
			$note = \Model_Notification::query()
			->where('id', $note_id)
			->where('to_id', $user->id)
			->get();

			if ($note)
			{
				$note[$note_id]->delete();
				return true;
			}
		}
		return Msg::failure('Failed to delete notification');
	}
	/**
	 * Returns all of the semesters from the semester table
	 *
	 */
	static public function semester_get()
	{
		return Semester::get_all();
	}

	static private function _validate_play_id($play_id)
	{
		$play = new Session_Play();
		$inst = self::_get_instance_for_play_id($play_id);
		if ($inst->playable_by_current_user())
		{
			if ($play->get_by_id($play_id))
			{
				if (intval($play->is_valid) == 1)
				{
					$play->update_elapsed(); // update the elapsed time
					return $play;
				}
			}
		}
		else
		{
			// invalidate the play
			if ($play->get_by_id($play_id)) $play->invalidate();
		}
		return false;
	}

	static protected function _decrypt_logs($logs)
	{
		// NOTE: this will need to have a session to have the secret key
		$num_logs = count($logs);
		for ($i = 0; $i < $num_logs; $i++)
		{
			if ($logs[$i]['encrypted'])
			{
				$logs[$i] = \Event::trigger('Materia.decrypt', $logs[$i]['data'], 'object');
				$logs[$i] = (array)$logs[$i];
			}
		}
		return $logs;
	}

	/**
	 * Gets a widget instance from a play id.
	 *
	 * @param int $play_id
	 *
	 * @return Widget_Instance The current widget instance.
	 */
	static private function _get_instance_for_play_id($play_id)
	{
		$play = new Session_Play();
		$play->get_by_id($play_id);
		$inst_id = $play->inst_id;
		if ( ! ($inst = Widget_Instance_Manager::get($inst_id))) throw new \HttpNotFoundException;
		return $inst;
	}
}
