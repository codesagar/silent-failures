# Post-write re-reading (renamed from 'read-back verification'; TRANSPARENCY item 10)

Script: readback.py (this file is the first committed derivation; the v1 numbers were
ad hoc and are shown for comparison). Definitions in the script docstring. Verification
and blind retry are NOT separable in this design; 'most-verifying model' claims are
retired in favor of 'most re-reading model'.

Tool-name classes observed in the arm (mechanical prefix mapping):
- WRITE: add_calendar_event_participants, add_user_to_channel, append_to_file, create_calendar_event, create_file, delete_file, invite_user_to_slack, post_webpage, remove_user_from_slack, reschedule_calendar_event, reserve_car_rental, reserve_hotel, schedule_transaction, send_channel_message, send_direct_message, send_email, send_money, share_file, update_password, update_scheduled_transaction, update_user_info
- READ: check_restaurant_opening_hours, get_all_car_rental_companies_in_city, get_all_hotels_in_city, get_all_restaurants_in_city, get_balance, get_car_fuel_options, get_car_price_per_day, get_car_rental_address, get_car_types_available, get_channels, get_contact_information_for_restaurants, get_cuisine_type_for_restaurants, get_current_day, get_day_calendar_events, get_dietary_restrictions_for_all_restaurants, get_draft_emails, get_file_by_id, get_flight_information, get_hotels_address, get_hotels_prices, get_iban, get_most_recent_transactions, get_price_for_restaurants, get_rating_reviews_for_car_rental, get_rating_reviews_for_hotels, get_rating_reviews_for_restaurants, get_received_emails, get_restaurants_address, get_scheduled_transactions, get_sent_emails, get_unread_emails, get_user_info, get_user_information, get_users_in_channel, get_webpage, list_files, read_channel_messages, read_file, read_inbox, search_calendar_events, search_contacts_by_email, search_contacts_by_name, search_emails, search_files, search_files_by_filename

| model | episodes w/ >=1 write | post-write re-read (any) | ...novel (function,args) | ...repeat-only | read-only episodes (excluded) | v1 stated |
|---|---|---|---|---|---|---|
| gpt-6-luna | 106 | 1.9% [0.4,5.9] | 1.9% [0.4,5.9] | 0.0% [0.0,2.3] | 185 | 2% |
| glm-5.3-flash | 147 | 8.2% [4.5,13.4] | 6.1% [3.1,10.9] | 2.0% [0.6,5.3] | 138 | 8% |
| kimi-k3 | 138 | 8.0% [4.3,13.4] | 3.6% [1.4,7.8] | 4.3% [1.8,8.7] | 137 | 8% |
| nemotron | 141 | 2.1% [0.6,5.6] | 1.4% [0.3,4.5] | 0.7% [0.1,3.3] | 133 | 3% |
| qwen-ablated | 166 | 29.5% [23.0,36.8] | 18.1% [12.8,24.4] | 11.4% [7.3,16.9] | 125 | 29% |
