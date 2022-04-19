import datetime
import re
import time
from typing import List, Optional

import praw
import praw.reddit
from tqdm import tqdm

import config


class RedditBot:
    def __init__(self):
        client_id = config.get_client_id()
        secret_key = config.get_secret_key()
        user_agent = "script by u/chutki03"
        username = config.get_username()
        password = config.get_password()
        self.r = praw.Reddit(
            client_id=client_id,
            client_secret=secret_key,
            user_agent=user_agent,
            redirect_uri="http://localhost:8080",
            username=username,
            password=password
        )
        print("Welcome to Reddit Bot..!")
        self.me = str(self.r.user.me())
        if username and password:
            self.get_bot_details()

    # bot
    def get_bot_details(self):
        print(f"user: {self.r.user.me().name}")
        print(self.r.user.me().id)

    # subreddit
    def get_details_of_subreddit(self, subreddit: str):
        details = self.r.subreddit(subreddit)
        print(f"display_name: {details.display_name}")
        print(f"_path: {details._path}")
        print(f"subscribers: {details.subscribers}")
        print(f"accounts_active: {details.accounts_active}")

    # comments & replies
    @staticmethod
    def get_comments_from_submission_obj(submission):
        """
        get only comments of submission
        :param submission: Submission
        :return:
        """
        return submission.comments

    def get_comments_with_timestamp(self, submission: str, minutes: int, sort_way: str = "new"):
        """
        get new comments of the subreddit
        """
        submission = self.r.submission(id=submission)
        submission.comment_sort = sort_way
        comments = submission.comments[:-1]
        comments.extend(map(lambda comment_id: self.r.comment(comment_id), submission.comments[-1].children))

        for comment in submission.comments.list():
            if hasattr(comment, 'created_utc') and (time.time() - comment.created_utc) / 60 < minutes:
                if hasattr(comment, 'body'):
                    print(f"{comment.author} {(time.time() - comment.created_utc) / 60} minutes- {comment.body}")

    def get_comments(self, submission: str, sort_way: str = "new"):
        """
        get top comments of the subreddit
        """
        submission = self.r.submission(id=submission)
        submission.comment_sort = sort_way
        comments = submission.comments[:-1]
        comments.extend(map(lambda comment_id: self.r.comment(comment_id), submission.comments[-1].children))
        top_comments = []
        for comment in comments:
            if hasattr(comment, 'body'):
                print(comment.body)
            top_comments.append(comment)

    @staticmethod
    def get_comments_with_replies(submission):
        """
        Get all comments including replies for a submission
        :param submission: Submission
        :return:
        """
        return submission.comments.list()

    def get_comments_of_subreddit(self, subreddit: str):
        """
        get comments for a subreddit with posts
        :param subreddit: str
        :return:
        """
        submissions = self.r.subreddit(subreddit)
        for submission in submissions.hot(limit=1):
            print("-" * 30)
            print(submission.title)
            for index, comment in enumerate(submission):
                if hasattr(comment, 'body'):
                    print('_' * 30)
                    print(comment.parent())
                    print(f"{comment.id}. {comment.body}")

    def search_for_comments(self, keywords: List[str], subreddits: List[str] = "all"):
        """
        search for comments with keywords given in given subreddits
        :param keywords: List[str]
        :param subreddits: List[str], all
        :return:
        """
        for comment in self.r.subreddit(subreddits).stream.comments():
            cbody = comment.body
            if any(keyword in cbody for keyword in keywords):
                print(cbody)

    def get_comments_upto_n_level(self, n: int, submission: str):
        """
        get comments upto specified sublevel from parent
        :param n: int max_level
        :param submission: str post id
        :return:
        """
        submission = self.r.submission(submission)
        self.get_comments_for_level(comments=submission.comments[:], max_level=n)

    def get_comments_for_level(self, max_level: int, comments, level=1):
        """
        get the comments order with sublevel comments

        :param max_level: int max level
        :param comments: list of comment objecs
        :param level: int current level
        :return:
        """
        if level <= max_level:
            for comment in comments:
                if hasattr(comment, "body"):
                    print("|" * (level - 1), comment.body)
                    self.get_comments_for_level(max_level=max_level, comments=comment.replies, level=level + 1)
                if level == 1:
                    print()

    def get_all_comments_without_stream(self, submission_id: str, minutes: int = None):
        from praw.models import MoreComments
        submission = self.r.submission("krntg6")
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=None)

        comments = True
        fetch = 1
        index = 1
        while comments:
            for comment in submission.comments.list():
                if isinstance(comment, MoreComments):
                    continue

                if minutes and hasattr(comment, 'created_utc') and (time.time() - comment.created_utc) / 60 > minutes:
                    continue

                check_author_of_comment = self.check_author_of_comment(comment)
                if comment.banned_by is not True and comment.body != '[deleted]' and check_author_of_comment:
                    if 'gpxkoun2' not in [re.author.id for re in comment.replies if re.author]:
                        print(index, comment.parent_id, comment.id, str(comment.author), comment.created_utc,
                              comment.body)
                        index += 1

            comments = bool(submission.comments.replace_more(limit=None))
            print(comments)
            print(f"Comments Done {fetch}")
            fetch += 1
            # if submission.comments.replace_more(limit=None):
            #     print("Getting Comments")
            #     comments = submission.comments.list()

    def reply_to_comment(self, comment_id: str, msg: str = "Random"):
        comment = self.r.comment(comment_id)
        comment.reply(msg)

    def add_comment_to_submissions(self, subreddit: str, keywords: [str]):
        submissions = self.r.subreddit(subreddit).hot(limit=5)
        for submission in submissions:
            if any(keyword in submission.selftext.lower() for keyword in keywords) or any(
                    keyword in submission.title for keyword in keywords):
                self.add_comment_to_submission(submission, comment="test comment, ignore")

    def get_submission(self, submission: str):
        submission = self.r.submission(submission)
        return submission

    def add_comment_to_submission(self, submission, comment: str):
        """

        :param submission: str or submission obj
        :param comment: str
        :return:
        """
        if type(submission) == str:
            submission = self.r.submission(submission)

        submission.reply(comment)

    def get_comments_from_stream(self, subreddit_id: str, **kwargs):
        """
        It gets all the comments of subreddit

        :param subreddit_id: str name of the subreddit
        :return:
        """
        minute_in_sec = 60
        skip_existing = kwargs.get("skip_existing", False)
        subreddit = self.r.subreddit(subreddit_id)

        epoch = datetime.datetime.fromtimestamp(self.r.auth.limits["reset_timestamp"])
        for comment in subreddit.stream.comments(skip_existing=skip_existing):
            if not comment.author == self.me:
                print(comment.id, comment.body)
            print(self.r.auth.limits)
            duration = (epoch - datetime.datetime.now()).total_seconds()
            if duration < minute_in_sec or self.get_remaining_hits() < 10:
                if duration <= 0:
                    duration = minute_in_sec
                print(duration)
                time.sleep(duration + 1)
                epoch = datetime.datetime.fromtimestamp(self.r.auth.limits["reset_timestamp"])

    def get_remaining_hits(self) -> int:
        remaining_hits = self.r.auth.limits
        return remaining_hits

    def get_comments_from_pushshift(self):
        # from pmaw import PushshiftAPI
        from psaw import PushshiftAPI
        api = PushshiftAPI()
        gen = api.search_comments(
            subreddit="ignr",
            before=int(datetime.datetime(2021, 11, 30, 0, 0, 0).timestamp()),
            after=int(datetime.datetime(2021, 11, 15, 0, 0, 0).timestamp()),
            limit=10
        )
        print("Fetching done..")
        comments = []
        for comment in gen:
            try:
                if comment.id in comments or comment.author.id == "fa169e4b":
                    continue
                print(comment.body)
                comments.append(comment)
            except Exception as e:
                print('error: ', e)
        print(comments)

    # submissions
    def get_posts_from_multiple_subreddit(self, subreddits: List[str]):
        """
        We can get posts from multiple reddits
        :param subreddits:
        :return:
        """

        # python+ml+datascience
        subreddits_arg = "+".join(subreddits)

        # time filter: all, year, month, week, day, hour
        submissions = self.r.subreddit(subreddits_arg).top("all")
        for submission in submissions:
            print(f"{submission.subreddit} - {submission.title}")

    def search_for_posts(self, subreddits: List[str], keywords: List[str], time_filter: str = None):
        """
        Get posts from subreddits, if any of the keywords match
        :param subreddits: List[str]
        :param keywords: List[str]
        :param time_filter: str hour, day, week, month, year
        :return:
        """
        sub_args = "+".join(subreddits)
        subreddits = self.r.subreddit(sub_args)
        subs = \
            subreddits.search(keywords, time_filter=time_filter) \
                if time_filter is not None else subreddits.search(keywords)

        for sub in subs:
            print(f"{sub.subreddit} | {sub.title}")

    def create_post(self, subreddit: str = "television"):
        self.r.subreddit(subreddit).submit(
            title="Best web series",
            selftext="For which webseries are you waiting for..? I am waiting for more series to come on WHAT IF? and Witcher. Maybe this post already have 100 characters. if not, now it will."
        )

    def add_post_with_image_to_subreddit(
            self, subreddit: str, title: str, image_path: str
    ):
        subreddit = self.r.subreddit(subreddit)
        subreddit.submit_image(
            title=title,
            image_path=image_path,
        )

    def reply_to_posts_in_pythonforengineers(self):
        import os
        if not os.path.isfile("posts_replied_to.txt"):
            posts_replied_to = []
        else:
            with open("posts_replied_to.txt", "r") as f:
                posts_replied_to = f.read()
                posts_replied_to = posts_replied_to.split("\n")
                posts_replied_to = list(filter(None, posts_replied_to))

        subreddit = self.r.subreddit('pythonforengineers')
        for submission in subreddit.hot():
            if submission.id not in posts_replied_to:
                if re.search("i love python", submission.title, re.IGNORECASE):
                    submission.reply("Chutki says: I love Python too!!")
                    print("Chutki replying to : ", submission.title)
                    posts_replied_to.append(submission.id)

        with open("posts_replied_to.txt", "w") as f:
            for post_id in posts_replied_to:
                f.write(post_id + "\n")

    def get_comments_of_user(
            self,
            user_name: str,
            sorting_way: str = "new",
            sorting_arg: Optional[str] = None,
            limit: int = 3000
    ):
        """
        Get comments of user
        :param limit:
        :param user_name: str
        :param sorting_way: new | top | hot
        :param sorting_arg: madatory for if sorting_way is top
        :parma limit:
        :return:
        """
        redditor = self.r.redditor(name=user_name)

        comments = []
        if sorting_way == "new":
            comments = redditor.comments.new(limit=limit)
        elif sorting_way == "hot":
            comments = redditor.comments.hot(limit=limit)
        if sorting_way == "top":
            comments = redditor.comments.top(sorting_arg, limit=limit)

        for index, comment in enumerate(comments):
            print("-" * 10)
            print(index)
            print("-" * 10)
            print(f"id: {comment.id}")
            print(f"body: {comment.body}")
            print(f"created_utc", {comment.created_utc})
            print(f"parent: {comment.parent_id}")
            print(f"subreddit: {comment.subreddit}")
            print(f"author: {comment.author}")
            print(f"submission_id: {comment.submission}")
            # print(f"submission: {comment.submission.title}") another api call
            print()
        print(self.r.auth.limits)

    def get_submissions_of_user(
            self,
            user_name: str,
            sorting_way: str = "new",
            sorting_arg: Optional[str] = None,
            limit: Optional[int] = 3000
    ):
        """
        Get submissions of user
        :param limit:
        :param user_name: str
        :param sorting_way: new | top | hot
        :param sorting_arg: madatory for if sorting_way is top
        :parma limit:
        :return:
        """
        redditor = self.r.redditor(name=user_name)
        submissions = []
        if sorting_way == "new":
            submissions = redditor.submissions.new(limit=limit)
        elif sorting_way == "top":
            submissions = redditor.submissions.top(sorting_arg, limit=limit)
        elif sorting_way == "hot":
            submissions = redditor.submissions.hot(limit=limit)

        for submission in submissions:
            print("-" * 10)
            print(f"title: {submission.title}")
            print(f"selftext: {submission.selftext}")
            print(f"author: {submission.author}")
            print(f"subreddit: {submission.subreddit}")
            print(f"num_comments: {submission.num_comments}")

    def check_author_of_comment(self, comment):
        return comment.author and not comment.author == self.me

    def get_comments_that_replied_multiple_times(self, submission_id: str, bot_name: str = None):
        from praw.models import MoreComments

        if bot_name is None:
            bot_name = self.me
        submission = self.r.submission(submission_id)
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=None)
        print(submission.title)

        comments = submission.comments.list()
        index = 1
        while comments:
            for comment in comments:
                if isinstance(comment, MoreComments):
                    continue

                if comment.banned_by is not True and comment.author and comment.author == bot_name:
                    print(index, comment.id, comment.author, comment.body)
                    index += 1
            comments = []
            if submission.comments.replace_more():
                comments = submission.comments.list()

    def get_analytics_of_bot(self, submission_id: str, bot_name: str = None):
        if bot_name is None:
            bot_name = self.me
        submission = self.r.submission(submission_id)
        submission.comment_sort = "new"
        submission.comments.replace_more(limit=None)
        print(submission.title)

        comments = submission.comments.list()

        print(f"{submission_id} has {len(comments)} comments in total...")
        self._get_number_of_replies(bot_name=bot_name, comments=comments)

    @staticmethod
    def _get_number_of_replies(bot_name: str, comments):
        from praw.models import MoreComments

        bot_replies = 1
        user_ids = []
        comment_data = [["comment_id", "author_name", "comment", "replies", "no_of_replies", "upvotes", "permlink"]]
        for comment in tqdm(comments):
            if isinstance(comment, MoreComments):
                continue

            if comment.banned_by is not True and comment.author:
                if comment.author == bot_name:
                    bot_replies += 1
                replies = list(map(lambda x: str(x), comment.replies.list()))
                comment_data .append([comment.id, comment.author, comment.body, '   '.join(replies), len(replies), comment.ups, comment.permalink])

        # with open("comment_data_v1.tsv", 'w') as f:
        #     f.write(comment_data)
        import csv

        with open('comment_data_v2.tsv', 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for row in comment_data:
                writer.writerow(row)

        print(f"{bot_name} have made {bot_replies} comments")


if __name__ == "__main__":
    bot = RedditBot()
    bot.get_analytics_of_bot(submission_id="ri8gbp", bot_name="SmellyBardBot")
